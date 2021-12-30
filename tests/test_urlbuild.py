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
Test url build method from url data objects.
"""

import unittest
import linkcheck.configuration
import linkcheck.director
import linkcheck.checker.urlbase
from linkcheck.checker import get_url_from
from . import has_windows


def get_test_aggregate():
    """
    Initialize a test configuration object.
    """
    config = linkcheck.configuration.Configuration()
    config["logger"] = config.logger_new("none")
    return linkcheck.director.get_aggregate(config)


class TestUrlBuild(unittest.TestCase):
    """
    Test url building.
    """

    def test_http_build(self):
        parent_url = "http://localhost:8001/tests/checker/data/http.html"
        base_url = "http://foo"
        recursion_level = 0
        aggregate = get_test_aggregate()
        o = get_url_from(base_url, recursion_level, aggregate, parent_url=parent_url)
        o.build_url()
        self.assertEqual(o.url, "http://foo")

    def test_urljoin(self):
        parent_url = "http://localhost:8001/test"
        base_url = ";param=value"
        res = linkcheck.checker.urlbase.urljoin(parent_url, base_url)
        self.assertEqual(res, "http://localhost:8001/;param=value")

    def test_urljoin_file(self):
        parent_url = "file:///a/b.html"
        base_url = "?c=d"
        recursion_level = 0
        aggregate = get_test_aggregate()
        o = get_url_from(base_url, recursion_level, aggregate, parent_url=parent_url)
        o.build_url()
        if has_windows():
            expected_url = "file:////a/b.html"
        else:
            expected_url = parent_url
        self.assertEqual(o.url, expected_url)

    def test_http_build2(self):
        parent_url = "http://example.org/test?a=b&c=d"
        base_url = "#usemap"
        recursion_level = 0
        aggregate = get_test_aggregate()
        o = get_url_from(base_url, recursion_level, aggregate, parent_url=parent_url)
        o.build_url()
        self.assertEqual(o.url, parent_url + base_url)
