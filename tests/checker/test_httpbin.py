# Copyright (C) 2014 Bastian Kleineidam
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
Test http stuff with httpbin.org.
"""
import re
from tests import need_network
from . import LinkCheckTest


def get_httpbin_url(path):
    """Get httpbin URL. Note that this also could be a local
    httpbin installation, but right now this uses the official site."""
    return "http://httpbin.org%s" % path


class TestHttpbin(LinkCheckTest):
    """Test http:// link redirection checking."""

    @need_network
    def test_http_link(self):
        linkurl = "http://www.example.com"
        nlinkurl = self.norm(linkurl)
        url = get_httpbin_url("/response-headers?Link=<%s>;rel=previous" % linkurl)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "warning The URL with content type 'application/json' is not parseable.",
            "valid",
            "url %s" % linkurl,
            "cache key %s" % nlinkurl,
            "real url %s" % nlinkurl,
            "name Link: header previous",
            "valid",
        ]
        self.direct(url, resultlines, recursionlevel=1)

    @need_network
    def test_basic_auth(self):
        user = "testuser"
        password = "testpassword"
        url = get_httpbin_url(f"/basic-auth/{user}/{password}")
        nurl = self.norm(url)
        entry = dict(user=user, password=password, pattern=re.compile(r".*"))
        confargs = dict(authentication=[entry])
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "valid",
        ]
        self.direct(url, resultlines, confargs=confargs)

    @need_network
    def test_http_refresh_header(self):
        linkurl = "http://www.example.com"
        nlinkurl = self.norm(linkurl)
        url = get_httpbin_url("/response-headers?Refresh=5;url=%s" % linkurl)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "warning The URL with content type 'application/json' is not parseable.",
            "valid",
            "url %s" % linkurl,
            "cache key %s" % nlinkurl,
            "real url %s" % nlinkurl,
            "name Refresh: header",
            "valid",
        ]
        self.direct(url, resultlines, recursionlevel=1)

    @need_network
    def test_http_content_location_header(self):
        linkurl = "http://www.example.com"
        nlinkurl = self.norm(linkurl)
        url = get_httpbin_url("/response-headers?Content-Location=%s" % linkurl)
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "warning The URL with content type 'application/json' is not parseable.",
            "valid",
            "url %s" % linkurl,
            "cache key %s" % nlinkurl,
            "real url %s" % nlinkurl,
            "name Content-Location: header",
            "valid",
        ]
        self.direct(url, resultlines, recursionlevel=1)
