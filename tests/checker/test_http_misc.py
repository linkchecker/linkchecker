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


class TestHttpMisc(HttpServerTest):
    """Test http:// misc link checking."""

    @need_network
    def test_html_internet(self):
        self.swf_test()
        self.file_test("sitemap.xml")

    def test_html(self):
        self.file_test("sitemapindex.xml")

    def swf_test(self):
        url = self.get_url("test.swf")
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
            "url http://www.example.org/",
            "cache key http://www.example.org/",
            "real url http://www.example.org/",
            "valid",
        ]
        self.direct(url, resultlines, recursionlevel=1)
