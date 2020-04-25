# Copyright (C) 2020 Chris Mayo
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
Test that <meta name="robots" content="nofollow"> is respected when using http
and ignored when checking a local file.
"""
from . import LinkCheckTest
from .httpserver import HttpServerTest

class TestHttpMetaRobots(HttpServerTest):
    """Test <meta name="robots" content="nofollow"> using http."""

    def test_http_meta_robots(self):
        url = "http://localhost:%d/tests/checker/data/norobots.html" % self.port
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid"
        ]
        self.direct(url, resultlines, recursionlevel=1)

class TestFileMetaRobots(LinkCheckTest):
    """Test <meta name="robots" content="nofollow"> from a file."""

    def test_file_meta_robots(self):
        datapath = "file://%(curdir)s/%(datadir)s/%%s" % self.get_attrs()
        url = datapath % "norobots.html"
        dncurl = datapath % "do_not_check.html"
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
            "url do_not_check.html",
            "cache key %s" % dncurl,
            "real url %s" % dncurl,
            "name bla",
            "error"
        ]
        self.direct(url, resultlines, recursionlevel=1)
