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
Test UrlBase.build_url()
"""
import unittest

import linkcheck.configuration
import linkcheck.director

from . import get_url_from


class TestBuildUrl(unittest.TestCase):
    """Test parsing of URLs by UrlBase.build_url()."""

    def test_build_url(self):
        config = linkcheck.configuration.Configuration()
        aggregate = linkcheck.director.get_aggregate(config)
        url = "https://user:password@host:1234/path/?key1=value1&key2=value2#fragment"
        url_data = get_url_from(url, 0, aggregate)
        self.assertEqual(url_data.scheme, "https")
        self.assertEqual(url_data.userinfo, "user:password")
        self.assertEqual(url_data.host, "host")
        self.assertEqual(url_data.port, 1234)
        self.assertEqual(url_data.anchor, "fragment")

        self.assertEqual(url_data.get_user_password(), ("user", "password"))

        # user without password
        url = "https://user@host/"
        url_data = get_url_from(url, 0, aggregate)
        self.assertEqual(url_data.userinfo, "user")

        # password without user
        url = "https://:password@host/"
        url_data = get_url_from(url, 0, aggregate)
        self.assertEqual(url_data.userinfo, ":password")

        # invalid port
        url = "https://host:abc/"
        url_data = get_url_from(url, 0, aggregate)
        self.assertFalse(url_data.valid)
