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
Test html anchor parsing and checking.
"""
from . import LinkCheckTest
from .httpserver import HttpServerTest


class TestAnchor(LinkCheckTest):
    """
    Test anchor checking of HTML pages.
    """

    def test_anchor(self):
        confargs = {"enabledplugins": ["AnchorCheck"]}
        url = "file://%(curdir)s/%(datadir)s/anchor.html" % self.get_attrs()
        nurl = self.norm(url)
        anchor = "broken"
        urlanchor = url + "#" + anchor
        resultlines = [
            "url %s" % urlanchor,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "warning Anchor `%s' (decoded: `%s') not found."
            " Available anchors: `myid:'." % (anchor, anchor),
            "valid",
        ]
        self.direct(urlanchor, resultlines, confargs=confargs)


class TestHttpAnchor(HttpServerTest):
    """
    Test checking of HTML pages containing links to anchors served over http.
    """

    def test_anchor_http(self):
        confargs = dict(enabledplugins=["AnchorCheck"], recursionlevel=1)
        self.file_test("http_anchor.html", confargs=confargs)


class TestEncodedAnchors(HttpServerTest):
    """Test HTML pages containing urlencoded links to anchors"""

    def test_anchor_encoded_http(self):
        """
        http://
        """
        confargs = dict(enabledplugins=["AnchorCheck"], recursionlevel=1)
        self.file_test("urlencoding_anchor.html", confargs=confargs)


class TestAnchorsAcrossMultipleFiles(HttpServerTest):
    """Test anchors when there are multiple HTML pages"""

    def test_anchor1_html(self):
        """
        Test a network of files that reference each other, starting with anchor1.html
        """
        confargs = dict(enabledplugins=["AnchorCheck"], recursionlevel=4)
        self.file_test("anchor1.html", confargs=confargs)
