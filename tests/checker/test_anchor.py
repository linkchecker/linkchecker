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


class TestFileAnchor(LinkCheckTest):
    """
    Test anchor checking of HTML files.
    """

    def test_anchor_file(self):
        confargs = {"enabledplugins": ["AnchorCheck"]}
        anchor = "broken"
        url = "file://%(curdir)s/%(datadir)s/anchor.html#%(anchor)s" % self.get_attrs(
               anchor=anchor)
        nurl = self.norm(url)
        resultlines = [
            f"url {url}",
            f"cache key {nurl}",
            f"real url {nurl}",
            f"warning Anchor `{anchor}' (decoded: `{anchor}') not found."
            " Available anchors: `myid:'.",
            "valid",
        ]
        self.direct(url, resultlines, confargs=confargs)


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

    def test_anchor_encoded_file(self):
        """
        file://
        This should have identical behavior as http://
        """
        filename = "urlencoding_anchor.html"
        confargs = {"enabledplugins": ["AnchorCheck"]}
        url = "file://%(curdir)s/%(datadir)s/%(filename)s" % self.get_attrs(
               filename=filename)
        # get results from the special result file that has `.file.` in its name
        resultlines = self.get_resultlines(f"{filename}.file")
        self.direct(url, resultlines, recursionlevel=1, confargs=confargs)


class TestAnchorsAcrossMultipleFiles(LinkCheckTest):
    """Test anchors when there are multiple files"""

    def test_anchor1_file(self):
        """
        Test a network of files that reference each other, starting with anchor1.html
        """
        filename = "anchor1.html"
        confargs = {"enabledplugins": ["AnchorCheck"]}
        url = "file://%(curdir)s/%(datadir)s/%(filename)s" % self.get_attrs(
               filename=filename)
        resultlines = self.get_resultlines(filename)
        self.direct(url, resultlines, recursionlevel=4, confargs=confargs)
