# Copyright (C) 2004-2012 Bastian Kleineidam
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
Test proxy handling.
"""

from unittest.mock import patch

from . import httpserver


class TestProxy(httpserver.HttpServerTest):
    """Test no_proxy env var handling."""

    def test_noproxy(self):
        with patch.dict("os.environ",
                        {
                            "http_proxy": "http://example.org:8877",
                            "no_proxy": "localhost:%d" % self.port,
                        }):
            self.noproxy_test()

    def noproxy_test(self):
        # Test setting proxy and no_proxy env variable.
        url = self.get_url("favicon.ico")
        nurl = url
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "info Ignoring proxy setting `http://example.org:8877'.",
            "valid",
        ]
        self.direct(url, resultlines, recursionlevel=0)
