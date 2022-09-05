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
from unittest.mock import patch
from linkcheck.htmlutil import linkparse

from . import LinkCheckTest
from .httpserver import HttpServerTest

class TestFileAnchor(LinkCheckTest):
    """ Simple test for a file:// URL """
    def test_anchor_file(self):
        confargs = {"enabledplugins": ["AnchorCheck"]}
        anchor = "broken"
        url = f"file://%(curdir)s/%(datadir)s/anchor.html#{anchor}" % self.get_attrs()
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "warning Anchor `%s' (decoded: `%s') not found. Available anchors: `myid:'." % (anchor, anchor),
            "valid",
        ]
        self.direct(url, resultlines, confargs=confargs)


class TestHttpAnchor(HttpServerTest):
    """ Simple test for a http:// URL """
    def test_anchor_http(self):
        confargs = dict(enabledplugins=["AnchorCheck"], recursionlevel=1)
        self.file_test("http_anchor.html", confargs=confargs)

class TestEncodedAnchors(HttpServerTest):
    """ Test HTML pages containing urlencoded links to anchors """

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
        url = f"file://%(curdir)s/%(datadir)s/{filename}" % self.get_attrs()
        resultlines = self.get_resultlines(f"{filename}.file") # get results from the special result file that has `.file.` in its name
        self.direct(url, resultlines, recursionlevel=1, confargs=confargs)

class TestAnchorsAcrossMultipleFiles(HttpServerTest):
    """ Test anchors when there are multiple files """

    def test_anchor1_file(self):
        """
        Test a group of files that reference each other, starting with anchor1.html
        """
        filename = "anchor1.html"
        confargs = {"enabledplugins": ["AnchorCheck"]}
        url = f"file://%(curdir)s/%(datadir)s/{filename}" % self.get_attrs()
        resultlines = self.get_resultlines(f"{filename}")
        self.direct(url, resultlines, recursionlevel=4, confargs=confargs)

    def test_caching_works(self):
        """
        Test the group with and without the cache, to see that the cache is working,
        and that we see the same results either way.
        """
        # setup the test data
        filename = "anchor1.html"
        confargs = {"enabledplugins": ["AnchorCheck"]}
        url = f"file://%(curdir)s/%(datadir)s/{filename}" % self.get_attrs()
        resultlines = self.get_resultlines(f"{filename}")

        # make a mock for linkparse.find_links that calls the original function,
        # so we can track call counts
        original_find_links = linkparse.find_links
        with patch("linkcheck.htmlutil.linkparse.find_links", autospec=True, side_effect=original_find_links) as proxy_find_links:
            # test with no cache
            confargs["anchorcachesize"] = 0
            self.direct(url, resultlines, recursionlevel=4, confargs=confargs)

            expected_call_count = 25  # I don't really know why it's "25"; it's just "way more" than the 3 URLs we are really processing
            actual_call_count = proxy_find_links.call_count
            if actual_call_count != expected_call_count:
                self.fail(f"expected (an absurd) {expected_call_count} find_links calls with the cache disabled, but got {actual_call_count}")

            # reset the mock
            proxy_find_links.call_count = 0

            # test with the cache enabled
            confargs["anchorcachesize"] = 3  # 3 should be just enough
            self.direct(url, resultlines, recursionlevel=4, confargs=confargs)

            # 3 for the basic URL processing plus 3 for the first time AnchorCheck sees each URL.
            # (3 total would be ideal)
            expected_call_count = 6
            actual_call_count = proxy_find_links.call_count
            if actual_call_count != expected_call_count:
                self.fail(f"expected {expected_call_count} find_links calls with the cache enabled, but got {actual_call_count}")

