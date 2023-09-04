# Copyright (C) 2000-2014 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
Main functions for link checking.
"""

import os
import html
import urllib.parse

from .. import url as urlutil, log, LOG_CHECK

MAX_FILESIZE = 1024 * 1024 * 10  # 10MB


def guess_url(url):
    """Guess if URL is a http or ftp URL.

    @param url: the URL to check
    @type url: unicode
    @return: url with *http://* or *ftp://* prepended if it's detected as
        a http respective ftp URL.
    @rtype: unicode
    """
    if url.lower().endswith(".html") and "/" not in url:
        return url
    if url.lower().startswith("www."):
        # syntactic sugar
        return f"http://{url}"
    elif url.lower().startswith("ftp."):
        # syntactic sugar
        return f"ftp://{url}"
    return url


def absolute_url(base_url, base_ref, parent_url):
    """
    Search for the absolute url to detect the link type. This does not
    join any url fragments together!

    @param base_url: base url from a link tag
    @type base_url: string or None
    @param base_ref: base url from <base> tag
    @type base_ref: string or None
    @param parent_url: url of parent document
    @type parent_url: string or None
    """
    if base_url and urlutil.url_is_absolute(base_url):
        return base_url
    elif base_ref and urlutil.url_is_absolute(base_ref):
        return base_ref
    elif parent_url and urlutil.url_is_absolute(parent_url):
        return parent_url
    return ""


def get_url_from(
    base_url,
    recursion_level,
    aggregate,
    parent_url=None,
    base_ref=None,
    line=None,
    column=None,
    page=0,
    name="",
    parent_content_type=None,
    extern=None,
    url_encoding=None,
):
    """
    Get url data from given base data.

    @param base_url: base url from a link tag
    @type base_url: string or None
    @param recursion_level: current recursion level
    @type recursion_level: number
    @param aggregate: aggregate object
    @type aggregate: aggregate.Consumer
    @param parent_url: parent url
    @type parent_url: string or None
    @param base_ref: base url from <base> tag
    @type base_ref: string or None
    @param line: line number
    @type line: number
    @param column: column number
    @type column: number
    @param page: page number
    @type page: number
    @param name: link name
    @type name: string
    @param extern: (is_extern, is_strict) or None
    @type extern: tuple(int, int) or None
    """
    if base_url is not None:
        # left strip for detection of URL scheme
        base_url_stripped = base_url.lstrip()
    else:
        base_url_stripped = base_url
    url = absolute_url(base_url_stripped, base_ref, parent_url).lower()
    if ":" in url:
        scheme = url.split(":", 1)[0].lower()
    else:
        scheme = None
        if not (url or name):
            # use filename as base url, with slash as path separator
            name = base_url.replace("\\", "/")
    allowed_schemes = aggregate.config["allowedschemes"]
    # ignore local PHP files with execution directives
    local_php = (
        parent_content_type == 'application/x-httpd-php'
        and '<?' in base_url
        and '?>' in base_url
        and scheme == 'file'
    )
    if local_php or (allowed_schemes and scheme not in allowed_schemes):
        klass = ignoreurl.IgnoreUrl
    else:
        assume_local_file = recursion_level == 0
        klass = get_urlclass_from(scheme, assume_local_file=assume_local_file)
        if "AnchorCheck" in aggregate.config["enabledplugins"] and \
                klass == fileurl.FileUrl:
            klass = fileurl.AnchorCheckFileUrl
    log.debug(LOG_CHECK, "%s handles url %s", klass.__name__, base_url)
    return klass(
        base_url,
        recursion_level,
        aggregate,
        parent_url=parent_url,
        base_ref=base_ref,
        line=line,
        column=column,
        page=page,
        name=name,
        extern=extern,
        url_encoding=url_encoding,
    )


def get_urlclass_from(scheme, assume_local_file=False):
    """Return checker class for given URL scheme. If the scheme
    cannot be matched and assume_local_file is True, assume a local file.
    """
    if scheme in ("http", "https"):
        klass = httpurl.HttpUrl
    elif scheme == "ftp":
        klass = ftpurl.FtpUrl
    elif scheme == "file":
        klass = fileurl.FileUrl
    elif scheme == "mailto":
        klass = mailtourl.MailtoUrl
    elif scheme == "dns":
        klass = dnsurl.DnsUrl
    elif scheme == "itms-services":
        klass = itmsservicesurl.ItmsServicesUrl
    elif scheme and unknownurl.is_unknown_scheme(scheme):
        klass = unknownurl.UnknownUrl
    elif assume_local_file:
        klass = fileurl.FileUrl
    else:
        klass = unknownurl.UnknownUrl
    return klass


def get_index_html(urls):
    """
    Construct artificial index.html from given URLs.

    @param urls: URL strings
    @type urls: iterator of string
    """
    lines = ["<html>", "<body>"]
    for entry in urls:
        name = html.escape(entry)
        try:
            url = html.escape(urllib.parse.quote(entry))
        except UnicodeEncodeError:
            log.warn(LOG_CHECK, "Unable to convert entry to Unicode")
            continue
        except KeyError:
            # Some unicode entries raise KeyError.
            url = name
        lines.append(f'<a href="{url}">{name}</a>')
    lines.extend(["</body>", "</html>"])
    return os.linesep.join(lines).encode()


# all the URL classes
from . import (  # noqa: E402
    fileurl,
    unknownurl,
    ftpurl,
    httpurl,
    dnsurl,
    mailtourl,
    ignoreurl,
    itmsservicesurl,
)
