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
from .httpserver import HttpServerTest, CookieRedirectHttpRequestHandler


class TestHttpsRedirect(HttpServerTest):
    """Test https:// link redirection checking."""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName=methodName)
        self.handler = RedirectHttpsRequestHandler

    def test_redirect(self):
        url = "http://localhost:%d/redirect1" % self.port
        nurl = url
        # rurl = "https://localhost:%d/newurl1" % self.port
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % url,
            # XXX the redirect fails because this is not an SSL server
            # "info Redirected to `%s'." % rurl.replace('http:', 'https:'),
            # "valid",
            # "url %s" % rurl,
            # "cache key %s" % rurl,
            # "real url %s" % rurl,
            "error",
        ]
        self.direct(url, resultlines, recursionlevel=0)


class RedirectHttpsRequestHandler(CookieRedirectHttpRequestHandler):
    def redirect(self):
        """Redirect request."""
        path = self.path.replace("redirect", "newurl")
        port = self.server.server_address[1]
        url = "https://localhost:%d%s" % (port, path)
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()
