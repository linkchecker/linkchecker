# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2014 Bastian Kleineidam
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
Test cookie routines.
"""

import os
import unittest

import linkcheck.cookies
import linkcheck.configuration
import linkcheck.director


class TestCookies (unittest.TestCase):
    """Test cookie routines."""

    def test_cookie_parse_multiple_headers (self):
        lines = [
            'Host: example.org',
            'Path: /hello',
            'Set-cookie: ID="smee"',
            'Set-cookie: spam="egg"',
        ]
        from_headers = linkcheck.cookies.from_headers
        cookies = from_headers("\r\n".join(lines))
        self.assertEqual(len(cookies), 2)
        for cookie in cookies:
            self.assertEqual(cookie.domain, "example.org")
            self.assertEqual(cookie.path, "/hello")
        self.assertEqual(cookies[0].name, 'ID')
        self.assertEqual(cookies[0].value, 'smee')
        self.assertEqual(cookies[1].name, 'spam')
        self.assertEqual(cookies[1].value, 'egg')

    def test_cookie_parse_multiple_values (self):
        lines = [
            'Host: example.org',
            'Set-cookie: baggage="elitist"; comment="hologram"',
        ]
        from_headers = linkcheck.cookies.from_headers
        cookies = from_headers("\r\n".join(lines))
        self.assertEqual(len(cookies), 2)
        for cookie in cookies:
            self.assertEqual(cookie.domain, "example.org")
            self.assertEqual(cookie.path, "/")
        self.assertEqual(cookies[0].name, 'baggage')
        self.assertEqual(cookies[0].value, 'elitist')
        self.assertEqual(cookies[1].name, 'comment')
        self.assertEqual(cookies[1].value, 'hologram')

    def test_cookie_parse_error (self):
        lines = [
            ' Host: imaweevil.org',
            'Set-cookie: baggage="elitist"; comment="hologram"',
        ]
        from_headers = linkcheck.cookies.from_headers
        self.assertRaises(ValueError, from_headers, "\r\n".join(lines))

    def test_cookie_file (self):
        # Regression test for https://github.com/linkcheck/linkchecker/issues/62
        config = linkcheck.configuration.Configuration()
        here = os.path.dirname(__file__)
        config['cookiefile'] = os.path.join(here, 'cookies.txt')
        aggregate = linkcheck.director.get_aggregate(config)
        aggregate.add_request_session()
        session = aggregate.get_request_session()
        self.assertEqual({c.name for c in session.cookies},
                         {'om', 'multiple', 'are'})
