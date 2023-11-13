# Copyright (C) 2005-2014 Bastian Kleineidam
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
Parsing of cookies.
"""

from http.cookiejar import split_header_words
import email
import requests

from . import LinkCheckerError


def from_file(filename):
    """Parse cookie data from a text file in HTTP header format.

    @return: list of tuples (headers, scheme, host, path)
    """
    entries = []
    with open(filename) as fd:
        lines = []
        for line in fd.readlines():
            line = line.rstrip()
            if not line:
                if lines:
                    entries.extend(from_headers("\r\n".join(lines)))
                lines = []
            else:
                lines.append(line)
        if lines:
            entries.extend(from_headers("\r\n".join(lines)))
        if not entries:
            raise LinkCheckerError(_("No entries found"))
        return entries


def from_headers(strheader):
    """Parse cookie data from a string in HTTP header (RFC 2616) format.

    @return: list of cookies
    @raises: ValueError for incomplete or invalid data
    """
    res = []
    headers = email.message_from_string(strheader)
    if "Host" not in headers:
        raise ValueError("Required header 'Host:' missing")
    host = headers["Host"]
    # XXX: our --help says we also pay attention to the Scheme: header,
    # but we don't?!
    path = headers.get("Path", "/")
    for headervalue in headers.get_all("Set-Cookie"):
        for pairs in split_header_words([headervalue]):
            for name, value in pairs:
                cookie = requests.cookies.create_cookie(
                    name, value, domain=host, path=path
                )
                res.append(cookie)
    return res
