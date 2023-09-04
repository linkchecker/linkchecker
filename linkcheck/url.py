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
Functions for parsing and matching URL strings.
"""

import os
import re
import urllib.parse

for scheme in ('ldap', 'irc'):
    if scheme not in urllib.parse.uses_netloc:
        urllib.parse.uses_netloc.append(scheme)

# The character set to encode non-ASCII characters in a URL. See also
# http://tools.ietf.org/html/rfc2396#section-2.1
# Note that the encoding is not really specified, but most browsers
# encode in UTF-8 when no encoding is specified by the HTTP headers,
# else they use the page encoding for followed link. See also
# http://code.google.com/p/browsersec/wiki/Part1#Unicode_in_URLs
url_encoding = "utf-8"

default_ports = {
    'http': 80,
    'https': 443,
    'ftp': 21,
}

# adapted from David Wheelers "Secure Programming for Linux and Unix HOWTO"
# http://www.dwheeler.com/secure-programs/Secure-Programs-HOWTO/\
# filter-html.html#VALIDATING-URIS
_path = r"\-\_\.\!\~\*\'\(\),"
_hex_safe = r"2-9a-f"
_hex_full = r"0-9a-f"
_part = r"([a-z0-9][-a-z0-9]{0,61}|[a-z])"
_safe_char = (
    fr"([a-z0-9{_path}\+]|"
    fr"(%[{_hex_safe}][{_hex_full}]))"
)
_safe_scheme_pattern = r"(https?|ftp)"
_safe_domain_pattern = fr"({_part}(\.{_part})*\.?)"
_safe_host_pattern = fr"{_safe_domain_pattern}(:(80|8080|8000|443))?"
_safe_path_pattern = (
    fr"((/([a-z0-9{_path}]|"
    fr"(%[{_hex_safe}][{_hex_full}]))+)*/?)"
)
_safe_fragment_pattern = fr"{_safe_char}*"
_safe_cgi = fr"{_safe_char}+(=({_safe_char}|/)+)?"
_safe_query_pattern = fr"({_safe_cgi}(&{_safe_cgi})*)?"
_safe_param_pattern = fr"({_safe_cgi}(;{_safe_cgi})*)?"
safe_url_pattern = r"{}://{}{}(#{})?".format(
    _safe_scheme_pattern,
    _safe_host_pattern,
    _safe_path_pattern,
    _safe_fragment_pattern,
)

is_safe_url = re.compile(f"(?i)^{safe_url_pattern}$").match
is_safe_domain = re.compile(f"(?i)^{_safe_domain_pattern}$").match


# snatched form urlparse.py
def splitparams(path):
    """Split off parameter part from path.
    Returns tuple (path-without-param, param)
    """
    if '/' in path:
        i = path.find(';', path.rfind('/'))
    else:
        i = path.find(';')
    if i < 0:
        return path, ''
    return path[:i], path[i + 1:]


def is_numeric_port(portstr):
    """return: integer port (== True) iff portstr is a valid port number,
           False otherwise
    """
    if portstr.isdigit():
        port = int(portstr)
        # 65536 == 2**16
        if 0 < port < 65536:
            return port
    return False


def parse_qsl(qs, encoding, keep_blank_values=0, strict_parsing=0):
    """Parse a query given as a string argument.

    @param qs: URL-encoded query string to be parsed
    @type qs: string
    @param keep_blank_values: flag indicating whether blank values in
        URL encoded queries should be treated as blank strings.  A
        true value indicates that blanks should be retained as blank
        strings.  The default false value indicates that blank values
        are to be ignored and treated as if they were  not included.
    @type keep_blank_values: bool
    @param strict_parsing: flag indicating what to do with parsing errors. If
        false (the default), errors are silently ignored. If true,
        errors raise a ValueError exception.
    @type strict_parsing: bool
    @returns: list of triples (key, value, separator) where key and value
      are the split CGI parameter and separator the used separator
      for this CGI parameter which is either a semicolon or an ampersand
    @rtype: list of triples
    """
    pairs = []
    name_value_amp = qs.split('&')
    for name_value in name_value_amp:
        if ';' in name_value:
            pairs.extend([x, ';'] for x in name_value.split(';'))
            pairs[-1][1] = '&'
        else:
            pairs.append([name_value, '&'])
    pairs[-1][1] = ''
    r = []
    for name_value, sep in pairs:
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            if strict_parsing:
                raise ValueError("bad query field: %r" % name_value)
            elif len(nv) == 1:
                # None value indicates missing equal sign
                nv = (nv[0], None)
            else:
                continue
        if nv[1] or keep_blank_values:
            name = urllib.parse.unquote(nv[0].replace('+', ' '), encoding=encoding)
            if nv[1]:
                value = urllib.parse.unquote(nv[1].replace('+', ' '), encoding=encoding)
            else:
                value = nv[1]
            r.append((name, value, sep))
    return r


def idna_encode(host):
    """Encode hostname as internationalized domain name (IDN) according
    to RFC 3490.
    @raise: UnicodeError if hostname is not properly IDN encoded.
    """
    if host:
        try:
            host.encode('ascii')
            return host, False
        except UnicodeError:
            uhost = host.encode('idna').decode('ascii')
            return uhost, uhost != host
    return host, False


def split_netloc(netloc):
    """Separate userinfo from host in urllib.parse.SplitResult.netloc.
    Originated as urllib.parse._splituser().
    """
    userinfo, delim, hostport = netloc.rpartition('@')
    return (userinfo if delim else None), hostport


def url_fix_host(urlparts, encoding):
    """Unquote and fix hostname. Returns is_idn."""
    if not urlparts[1]:
        urlparts[2] = urllib.parse.unquote(urlparts[2], encoding=encoding)
        return False
    userpass, hostport = split_netloc(urlparts[1])
    if userpass:
        userpass = urllib.parse.unquote(userpass, encoding=encoding)
    netloc, is_idn = idna_encode(
        urllib.parse.unquote(hostport, encoding=encoding).lower()
    )
    # a leading backslash in path causes urlsplit() to add the
    # path components up to the first slash to host
    # try to find this case...
    i = netloc.find("\\")
    if i != -1:
        # ...and fix it by prepending the misplaced components to the path
        comps = netloc[i:]  # note: still has leading backslash
        if not urlparts[2] or urlparts[2] == '/':
            urlparts[2] = comps
        else:
            urlparts[2] = "{}{}".format(
                comps,
                urllib.parse.unquote(urlparts[2], encoding=encoding),
            )
        netloc = netloc[:i]
    else:
        # a leading ? in path causes urlsplit() to add the query to the
        # host name
        i = netloc.find("?")
        if i != -1:
            netloc, urlparts[3] = netloc.split('?', 1)
        # path
        urlparts[2] = urllib.parse.unquote(urlparts[2], encoding=encoding)
    if userpass:
        # append AT for easy concatenation
        userpass += "@"
    else:
        userpass = ""
    if urlparts[0] in default_ports:
        dport = default_ports[urlparts[0]]
        host, port = splitport(netloc, port=dport)
        if host.endswith("."):
            host = host[:-1]
        if port != dport:
            host = f"{host}:{port}"
        netloc = host
    urlparts[1] = userpass + netloc
    return is_idn


def url_fix_mailto_urlsplit(urlparts):
    """Split query part of mailto url if found."""
    sep = "?"
    if sep in urlparts[2]:
        urlparts[2], urlparts[3] = urlparts[2].split(sep, 1)


# wayback urls include in the path http[s]://. By default the
# tidying mechanism in linkchecker encodes the : and deletes the second slash
# This function reverses these corrections. This function expects only the
# path section of the URL as input.
wayback_regex = re.compile(r'(https?)(\%3A/|:/)')


def url_fix_wayback_query(path):
    return wayback_regex.sub(r'\1://', path)


def url_parse_query(query, encoding):
    """Parse and re-join the given CGI query."""
    # if ? is in the query, split it off, seen at msdn.microsoft.com
    append = ""
    while '?' in query:
        query, rest = query.rsplit('?', 1)
        append = '?' + url_parse_query(rest, encoding=encoding) + append
    f = []
    for k, v, sep in parse_qsl(query, keep_blank_values=True, encoding=encoding):
        k = urllib.parse.quote(k, safe='/-:,;')
        if v:
            v = urllib.parse.quote(v, safe='/-:,;')
            f.append(f"{k}={v}{sep}")
        elif v is None:
            f.append(f"{k}{sep}")
        else:
            # some sites do not work when the equal sign is missing
            f.append(f"{k}={sep}")
    return ''.join(f) + append


def urlunsplit(urlparts):
    """Same as urllib.parse.urlunsplit but with extra UNC path handling
    for Windows OS."""
    res = urllib.parse.urlunsplit(urlparts)
    if os.name == 'nt' and urlparts[0] == 'file' and '|' not in urlparts[2]:
        # UNC paths must have 4 slashes: 'file:////server/path'
        # Depending on the path in urlparts[2], urllib.parse.urlunsplit()
        # left only two or three slashes. This is fixed below
        repl = 'file://' if urlparts[2].startswith('//') else 'file:/'
        res = res.replace('file:', repl)
    return res


def url_norm(url, encoding):
    """Normalize the given URL which must be quoted. Supports unicode
    hostnames (IDNA encoding) according to RFC 3490.

    @return: (normed url, idna flag)
    @rtype: tuple of length two
    """
    urlparts = list(urllib.parse.urlsplit(url))
    # scheme
    urlparts[0] = urllib.parse.unquote(urlparts[0], encoding=encoding).lower()
    # mailto: urlsplit is broken
    if urlparts[0] == 'mailto':
        url_fix_mailto_urlsplit(urlparts)
    # host (with path or query side effects)
    is_idn = url_fix_host(urlparts, encoding)
    # query
    urlparts[3] = url_parse_query(urlparts[3], encoding=encoding)
    if urlparts[0] in urllib.parse.uses_relative:
        # URL has a hierarchical path we should norm
        if not urlparts[2]:
            # Empty path is allowed if both query and fragment are also empty.
            # Note that in relative links, urlparts[0] might be empty.
            # In this case, do not make any assumptions.
            if urlparts[0] and (urlparts[3] or urlparts[4]):
                urlparts[2] = '/'
        else:
            # fix redundant path parts
            urlparts[2] = collapse_segments(urlparts[2])
    # anchor
    urlparts[4] = urllib.parse.unquote(urlparts[4], encoding=encoding)
    # quote parts again
    urlparts[0] = urllib.parse.quote(urlparts[0])  # scheme
    urlparts[1] = urllib.parse.quote(urlparts[1], safe='@:')  # host
    urlparts[2] = urllib.parse.quote(urlparts[2], safe=_nopathquote_chars)  # path
    if not urlparts[0].startswith("feed"):
        # unencode colon in http[s]:// in wayback path
        urlparts[2] = url_fix_wayback_query(urlparts[2])
    urlparts[4] = urllib.parse.quote(urlparts[4], safe="!$&'()*+,-./;=?@_~")  # anchor
    res = urlunsplit(urlparts)
    if url.endswith('#') and not urlparts[4]:
        # re-append trailing empty fragment
        res += '#'
    return (res, is_idn)


_slashes_ro = re.compile(r"/+")
_thisdir_ro = re.compile(r"^\./")
_samedir_ro = re.compile(r"/\./|/\.$")
_parentdir_ro = re.compile(r"^/(\.\./)+|/(?!\.\./)[^/]+/\.\.(/|$)")
_relparentdir_ro = re.compile(r"^(?!\.\./)[^/]+/\.\.(/|$)")


def collapse_segments(path):
    """Remove all redundant segments from the given URL path.
    Precondition: path is an unquoted url path"""
    # replace backslashes
    # note: this is _against_ the specification (which would require
    # backslashes to be left alone, and finally quoted with '%5C')
    # But replacing has several positive effects:
    # - Prevents path attacks on Windows systems (using \.. parent refs)
    # - Fixes bad URLs where users used backslashes instead of slashes.
    #   This is a far more probable case than users having an intentional
    #   backslash in the path name.
    path = path.replace('\\', '/')
    # shrink multiple slashes to one slash
    path = _slashes_ro.sub("/", path)
    # collapse redundant path segments
    path = _thisdir_ro.sub("", path)
    path = _samedir_ro.sub("/", path)
    # collapse parent path segments
    # note: here we exploit the fact that the replacements happen
    # to be from left to right (see also _parentdir_ro above)
    newpath = _parentdir_ro.sub("/", path)
    while newpath != path:
        path = newpath
        newpath = _parentdir_ro.sub("/", path)
    # collapse parent path segments of relative paths
    # (ie. without leading slash)
    newpath = _relparentdir_ro.sub("", path)
    while newpath != path:
        path = newpath
        newpath = _relparentdir_ro.sub("", path)
    return path


url_is_absolute = re.compile(r"^[-\.a-z]+:", re.I).match


def url_quote(url, encoding):
    """Quote given URL."""
    if not url_is_absolute(url):
        return document_quote(url)
    urlparts = list(urllib.parse.urlsplit(url))
    urlparts[0] = urllib.parse.quote(urlparts[0])  # scheme
    urlparts[1] = urllib.parse.quote(urlparts[1], safe=':')  # host
    urlparts[2] = urllib.parse.quote(urlparts[2], safe='/=,')  # path
    urlparts[3] = urllib.parse.quote(urlparts[3], safe='&=,')  # query
    f = []
    for k, v, sep in parse_qsl(
        urlparts[3], encoding=encoding, keep_blank_values=True
    ):  # query
        k = urllib.parse.quote(k, safe='/-:,;')
        if v:
            v = urllib.parse.quote(v, safe='/-:,;')
            f.append(f"{k}={v}{sep}")
        else:
            f.append(f"{k}{sep}")
    urlparts[3] = ''.join(f)
    urlparts[4] = urllib.parse.quote(urlparts[4])  # anchor
    return urlunsplit(urlparts)


def document_quote(document):
    """Quote given document."""
    doc, delim, query = document.rpartition('?')
    if not delim:
        doc = document
        query = None
    doc = urllib.parse.quote(doc, safe='/=,')
    if query:
        return f"{doc}?{query}"
    return doc


_nopathquote_chars = "-;/=,~*+()@!"
if os.name == 'nt':
    _nopathquote_chars += "|"
_safe_url_chars = re.escape(_nopathquote_chars + "_:.&#%?[]!") + "a-zA-Z0-9"
_safe_url_chars_ro = re.compile(fr"^[{_safe_url_chars}]*$")


def url_needs_quoting(url):
    """Check if url needs percent quoting. Note that the method does
    only check basic character sets, and not any other syntax.
    The URL might still be syntactically incorrect even when
    it is properly quoted.
    """
    if url.rstrip() != url:
        # handle trailing whitespace as a special case
        # since '$' matches immediately before a end-of-line
        return True
    return not _safe_url_chars_ro.match(url)


def splitport(host, port=0):
    """Split optional port number from host. If host has no port number,
    the given default port is returned.

    @param host: host name
    @type host: string
    @param port: the port number (default 0)
    @type port: int

    @return: tuple of (host, port)
    @rtype: tuple of (string, int)
    """
    if ":" in host:
        shost, sport = host.split(":", 1)
        iport = is_numeric_port(sport)
        if iport:
            host, port = shost, iport
        elif not sport:
            # empty port, ie. the host was "hostname:"
            host = shost
        else:
            # For an invalid non-empty port leave the host name as is
            pass
    return host, port
