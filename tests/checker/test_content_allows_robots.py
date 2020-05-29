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
Also test different values of the content attribute are correctly matched.
"""
import unittest

import linkcheck.configuration
import linkcheck.director
from linkcheck.htmlutil.htmlsoup import make_soup
from . import get_url_from

from . import LinkCheckTest
from .httpserver import HttpServerTest


class TestHttpMetaRobots(HttpServerTest):
    """Test <meta name="robots" content="nofollow"> using http."""

    def test_http_meta_robots(self):
        url = self.get_url("norobots.html")
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
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
            "error",
        ]
        self.direct(url, resultlines, recursionlevel=1)


class TestMetaRobotsVariants(unittest.TestCase):
    """Test different values of the robots meta directive content attribute"""

    def test_nofollow_variants(self):
        config = linkcheck.configuration.Configuration()
        aggregate = linkcheck.director.get_aggregate(config)
        url = "http://example.org"
        url_data = get_url_from(url, 0, aggregate)
        url_data.content_type = "text/html"

        url_data.soup = make_soup('<meta name="robots" content="nofollow">')
        self.assertFalse(url_data.content_allows_robots())

        url_data.soup = make_soup(
            '<meta name="robots" content="nocache, Nofollow, noimageindex">'
        )
        self.assertFalse(url_data.content_allows_robots())

        url_data.soup = make_soup('<meta name="robots" content="noindex, follow">')
        self.assertTrue(url_data.content_allows_robots())
