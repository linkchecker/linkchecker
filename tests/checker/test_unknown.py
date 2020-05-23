# Copyright (C) 2010-2014 Bastian Kleineidam
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
Test checking of unknown URLs.
"""
from . import LinkCheckTest


class TestUnknown(LinkCheckTest):
    """Test unknown URL scheme checking."""

    def test_skype(self):
        url = "skype:"
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "info Skype URL ignored.",
            "valid",
        ]
        self.direct(url, resultlines)

    def test_irc(self):
        url = "irc://example.org"
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "info Irc URL ignored.",
            "valid",
        ]
        self.direct(url, resultlines)
        url = "ircs://example.org"
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "info Ircs URL ignored.",
            "valid",
        ]
        self.direct(url, resultlines)

    def test_steam(self):
        url = "steam://connect/example.org"
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "info Steam URL ignored.",
            "valid",
        ]
        self.direct(url, resultlines)

    def test_feed(self):
        url = "feed:https://example.com/entries.atom"
        nurl = "feed:https%3A/example.com/entries.atom"
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "info Feed URL ignored.",
            "valid",
        ]
        self.direct(url, resultlines)
        url = "feed://example.com/entries.atom"
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "info Feed URL ignored.",
            "valid",
        ]
        self.direct(url, resultlines)
