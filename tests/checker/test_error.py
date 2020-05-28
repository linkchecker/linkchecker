# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2014 Bastian Kleineidam
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
Test error checking.
"""
from . import LinkCheckTest


class TestError(LinkCheckTest):
    """
    Test unrecognized or syntactically wrong links.
    """

    def test_unrecognized(self):
        # Unrecognized scheme
        url = "hutzli:"
        attrs = self.get_attrs(url=url)
        attrs["nurl"] = self.norm("file://%(curdir)s/%(url)s" % attrs)
        resultlines = [
            "url file://%(curdir)s/%(url)s" % attrs,
            "cache key %(nurl)s" % attrs,
            "real url %(nurl)s" % attrs,
            "error",
        ]
        self.direct(url, resultlines)

    def test_invalid1(self):
        # invalid scheme chars
        url = "äöü:"
        attrs = self.get_attrs(url=url)
        attrs["nurl"] = self.norm("file://%(curdir)s/%(url)s" % attrs)
        resultlines = [
            "url file://%(curdir)s/%(url)s" % attrs,
            "cache key %(nurl)s" % attrs,
            "real url %(nurl)s" % attrs,
            "name %(url)s" % attrs,
            "error",
        ]
        self.direct(url, resultlines)

    def test_invalid2(self):
        # missing scheme alltogether
        url = "äöü"
        attrs = self.get_attrs(url=url)
        attrs["nurl"] = self.norm("file://%(curdir)s/%(url)s" % attrs)
        resultlines = [
            "url file://%(curdir)s/%(url)s" % attrs,
            "cache key %(nurl)s" % attrs,
            "real url %(nurl)s" % attrs,
            "name %(url)s" % attrs,
            "error",
        ]
        self.direct(url, resultlines)

    def test_invalid3(self):
        # really fucked up
        url = "@³²¼][½ ³@] ¬½"
        attrs = self.get_attrs(url=url)
        attrs["nurl"] = self.norm("file://%(curdir)s/%(url)s" % attrs)
        resultlines = [
            "url file://%(curdir)s/%(url)s" % attrs,
            "cache key %(nurl)s" % attrs,
            "real url %(nurl)s" % attrs,
            "name %(url)s" % attrs,
            "error",
        ]
        self.direct(url, resultlines)
