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


class TestHttpRedirect(HttpServerTest):
    """Test http:// link redirection checking."""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName=methodName)
        self.handler = CookieRedirectHttpRequestHandler

    @need_network
    def test_redirect(self):
        self.redirect1()
        self.redirect2()
        self.redirect3()
        self.redirect4()
        self.redirect5()

    def redirect1(self):
        url = "http://localhost:%d/redirect1" % self.port
        nurl = url
        rurl = url.replace("redirect", "newurl")
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % rurl,
            "info Redirected to `%s'." % rurl,
            "error",
        ]
        self.direct(url, resultlines, recursionlevel=0)

    def redirect2(self):
        url = self.get_url("redirect.html")
        nurl = url
        rurl = url.replace("redirect", "newurl")
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % rurl,
            "info Redirected to `%s'." % rurl,
            "valid",
        ]
        self.direct(url, resultlines, recursionlevel=99)

    def redirect3(self):
        url = "http://localhost:%d/tests/checker/data/redir.html" % self.port
        resultlines = self.get_resultlines("redir.html")
        self.direct(url, resultlines, recursionlevel=1)

    def redirect4(self):
        url = "http://localhost:%d/redirect_newscheme_ftp" % self.port
        nurl = url
        # rurl = "ftp://example.com/"
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            # don't allow ftp redirects
            # "info Redirected to `%s'." % rurl,
            # "valid",
            # "url %s" % rurl,
            # "cache key %s" % rurl,
            # "real url %s" % rurl,
            "error",
        ]
        self.direct(url, resultlines, recursionlevel=99)

    def redirect5(self):
        url = "http://localhost:%d/redirect_newscheme_file" % self.port
        nurl = url
        # rurl = "file:README"
        # rnurl = "file:///README"
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            # don't allow file redirects
            # "info Redirected to `%s'." % rurl,
            # "warning Redirection to url `%s' is not allowed." % rnurl,
            "error",
        ]
        self.direct(url, resultlines, recursionlevel=99)

    def redirect6(self):
        # max_redirect = 10
        # url = "http://httpbin.org/redirect/" + max_redirect --> valid
        # url = "http://httpbin.org/redirect/" + (max_redirect+1) --> error
        pass  # XXX
