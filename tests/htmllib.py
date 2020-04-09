# -*- coding: iso-8859-1 -*-
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
HTML parser handler test class.
"""

import sys


class HtmlPrettyPrinter:
    """
    Print out all parsed HTML data in encoded form.
    Also stores error and warnings messages.
    """

    def __init__ (self, fd=sys.stdout, encoding="iso8859-1"):
        """
        Write to given file descriptor in given encoding.

        @param fd: file like object (default=sys.stdout)
        @type fd: file
        @param encoding: encoding (default=iso8859-1)
        @type encoding: string
        """
        self.fd = fd
        self.encoding = encoding

    def start_element (self, tag, attrs, element_text, lineno, column):
        """
        Print HTML start element.

        @param tag: tag name
        @type tag: string
        @param attrs: tag attributes
        @type attrs: dict
        @return: None
        """
        self.fd.write("<%s" % tag.replace("/", ""))
        for key, val in sorted(attrs.items()):
            if val is None:
                self.fd.write(" %s" % key)
            else:
                self.fd.write(' %s="%s"' % (key, quote_attrval(val)))
        if element_text:
            self.fd.write(">%s</%s>" % (element_text, tag))
        else:
            self.fd.write("/>")


def quote_attrval (s):
    """
    Quote a HTML attribute to be able to wrap it in double quotes.

    @param s: the attribute string to quote
    @type s: string
    @return: the quoted HTML attribute
    @rtype: string
    """
    res = []
    for c in s:
        if ord(c) <= 127:
            # ASCII
            if c == '&':
                res.append("&amp;")
            elif c == '"':
                res.append("&quot;")
            else:
                res.append(c)
        else:
            res.append("&#%d;" % ord(c))
    return "".join(res)
