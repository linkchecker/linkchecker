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

from tests import need_network
from .httpserver import HttpServerTest, CookieRedirectHttpRequestHandler


class TestHttp(HttpServerTest):
    """Test http:// link checking."""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName=methodName)
        self.handler = CookieRedirectHttpRequestHandler

    @need_network
    def test_html_internet(self):
        confargs = dict(recursionlevel=1)
        self.file_test("http.html", confargs=confargs)
        self.file_test("http_lowercase.html", confargs=confargs)
        self.file_test("http_quotes.html", confargs=confargs)
        self.file_test("http_slash.html", confargs=confargs)
        self.file_test("http_url_quote.html", confargs=confargs)

    def test_html(self):
        confargs = dict(recursionlevel=1)
        self.file_test("http_empty.html", confargs=confargs)
        self.file_test("http_file.html", confargs=confargs)
        self.file_test("http_utf8.html", confargs=confargs)
        self.file_test("http.xhtml", confargs=confargs)
        self.file_test("http_invalid_host.html", confargs=confargs)

    def test_status(self):
        for status in sorted(self.handler.responses.keys()):
            self._test_status(status)

    def _test_status(self, status):
        url = "http://localhost:%d/status/%d" % (self.port, status)
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
        ]
        if status in (204,):
            resultlines.append("warning No Content")
        if status == 429:
            resultlines.append("warning Rate limited (Retry-After: None)")
        if (status not in [101, 102, 103] and status < 200) or (
            status >= 400 and status != 429
        ):
            result = "error"
        else:
            result = "valid"
        resultlines.append(result)
        self.direct(url, resultlines, recursionlevel=0)
