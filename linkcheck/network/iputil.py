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

import ipaddress
import re
import socket
from .. import log, LOG_CHECK


def is_valid_ip(ip):
    """
    Return True if given ip is a valid IPv4 or IPv6 address.
    """
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return False
    return True


def resolve_host(host):
    """
    Return list of ip numbers for given host.

    @param host: hostname or IP address
    """
    ips = []
    try:
        for res in socket.getaddrinfo(host, None, 0, socket.SOCK_STREAM):
            # res is a tuple (address family, socket type, protocol,
            #  canonical name, socket address)
            # add first ip of socket address
            ips.append(res[4][0])
    except OSError:
        log.info(LOG_CHECK, "Ignored invalid host %r", host)
    return ips


is_obfuscated_ip = re.compile(r"^(0x[a-f0-9]+|[0-9]+)$").match
