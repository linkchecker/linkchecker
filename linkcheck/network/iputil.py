# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2014 Bastian Kleineidam
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
Ip number related utility functions.
"""

import re
import socket
from .. import log, LOG_CHECK


# IP Adress regular expressions
# Note that each IPv4 octet can be encoded in dezimal, hexadezimal and octal.
_ipv4_num = r"\d{1,3}"
# XXX
_ipv4_num_4 = r"%s\.%s\.%s\.%s" % ((_ipv4_num,) * 4)
_ipv4_re = re.compile(r"^%s$" % _ipv4_num_4)


# IPv6; See also rfc2373
_ipv6_num = r"[\da-f]{1,4}"
_ipv6_re = re.compile(r"^%s:%s:%s:%s:%s:%s:%s:%s$" % ((_ipv6_num,) * 8))
_ipv6_ipv4_re = re.compile(r"^%s:%s:%s:%s:%s:%s:" % ((_ipv6_num,) * 6) + \
                           r"%s$" % _ipv4_num_4)
_ipv6_abbr_re = re.compile(r"^((%s:){0,6}%s)?::((%s:){0,6}%s)?$" % \
                            ((_ipv6_num,) * 4))
_ipv6_ipv4_abbr_re = re.compile(r"^((%s:){0,4}%s)?::((%s:){0,5})?" % \
                           ((_ipv6_num,) * 3) + \
                           "%s$" % _ipv4_num_4)


def is_valid_ip (ip):
    """
    Return True if given ip is a valid IPv4 or IPv6 address.
    """
    return is_valid_ipv4(ip) or is_valid_ipv6(ip)


def is_valid_ipv4 (ip):
    """
    Return True if given ip is a valid IPv4 address.
    """
    if not _ipv4_re.match(ip):
        return False
    a, b, c, d = [int(i) for i in ip.split(".")]
    return a <= 255 and b <= 255 and c <= 255 and d <= 255


def is_valid_ipv6 (ip):
    """
    Return True if given ip is a valid IPv6 address.
    """
    # XXX this is not complete: check ipv6 and ipv4 semantics too here
    if not (_ipv6_re.match(ip) or _ipv6_ipv4_re.match(ip) or
            _ipv6_abbr_re.match(ip) or _ipv6_ipv4_abbr_re.match(ip)):
        return False
    return True


def resolve_host (host):
    """
    @host: hostname or IP address
    Return list of ip numbers for given host.
    """
    ips = []
    try:
        for res in socket.getaddrinfo(host, None, 0, socket.SOCK_STREAM):
            # res is a tuple (address family, socket type, protocol,
            #  canonical name, socket address)
            # add first ip of socket address
            ips.append(res[4][0])
    except socket.error:
        log.info(LOG_CHECK, "Ignored invalid host %r", host)
    return ips


is_obfuscated_ip = re.compile(r"^(0x[a-f0-9]+|[0-9]+)$").match
