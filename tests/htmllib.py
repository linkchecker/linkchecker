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
HTML parser test function.
"""


def pretty_print_html(fd, soup):
    """
    Print out all parsed HTML data,
    writing to the given file descriptor.

    @param fd: file like object
    @type fd: file
    @param soup: BeautifulSoup object
    @type soup: BeautifulSoup
    """
    for element in soup.find_all(True):
        tag = element.name
        element_text = element.text.strip()

        fd.write("<%s" % tag.replace("/", ""))
        for key, val in sorted(element.attrs.items()):
            if val is None:
                fd.write(" %s" % key)
            else:
                fd.write(f' {key}="{quote_attrval(val)}"')
        if element_text:
            fd.write(f">{element_text}</{tag}>")
        else:
            fd.write("/>")


def quote_attrval(s):
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
            if c == "&":
                res.append("&amp;")
            elif c == '"':
                res.append("&quot;")
            else:
                res.append(c)
        else:
            res.append("&#%d;" % ord(c))
    return "".join(res)
