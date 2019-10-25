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
Test http checking.
"""
from .httpserver import HttpServerTest
from tests import need_network

class TestHttpMisc (HttpServerTest):
    """Test http:// misc link checking."""

    @need_network
    def test_html (self):
        self.swf_test()
        self.file_test("sitemap.xml")

    def swf_test (self):
        url = self.get_url(u"test.swf")
        resultlines = [
            u"url %s" % url,
            u"cache key %s" % url,
            u"real url %s" % url,
            u"valid",
            u"url http://www.example.org/",
            u"cache key http://www.example.org/",
            u"real url http://www.example.org/",
            u"valid",
        ]
        self.direct(url, resultlines, recursionlevel=1)
