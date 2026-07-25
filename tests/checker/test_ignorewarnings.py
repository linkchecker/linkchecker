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
Test ignoring of warnings.
"""

from re import compile as re_compile
from types import SimpleNamespace

from linkcheck.checker.urlbase import UrlBase

from . import LinkCheckTest


class TestIgnoreWarnings(LinkCheckTest):
    """
    Test whether ignoring of warnings per URL works.
    """

    def test_given_warning_for_given_url_ignored(self):
        confargs = {
            "ignorewarningsforurls": [
                (re_compile("test.txt"), re_compile("url-content-size-zero"))
            ]
        }
        self.file_test("base_ignorewarnings.html", confargs=confargs)

    def test_warning_for_unmatching_url_not_ignored(self):
        confargs = {
            "ignorewarningsforurls": [
                (re_compile("test_incorrect.txt"), re_compile("url-content-size-zero"))
            ]
        }
        self.file_test("base_ignorewarnings_with_warning.html", confargs=confargs)

    def test_non_matching_warning_for_matching_url_not_ignored(self):
        confargs = {
            "ignorewarningsforurls": [
                (re_compile("test.txt"), re_compile("not-a-warning"))
            ]
        }
        self.file_test("base_ignorewarnings_with_warning.html", confargs=confargs)

    def test_empty_warning_spec_matches_anything(self):
        confargs = {
            "ignorewarningsforurls": [
                (re_compile("test.txt"), re_compile(""))
            ]
        }
        self.file_test("base_ignorewarnings.html", confargs=confargs)


class TestIgnoreWarningsBeforeUrlBuilt(LinkCheckTest):
    """
    Test that warnings added before the real URL is built do not crash.
    """

    def test_warning_before_url_is_built(self):
        """A warning can be added while self.url is still None."""
        url_data = UrlBase.__new__(UrlBase)
        url_data.reset()
        url_data.aggregate = SimpleNamespace(
            config={
                "ignorewarnings": [],
                "ignorewarningsforurls": [
                    (re_compile("^https://youtu.be"), re_compile("url-whitespace"))
                ],
            }
        )
        self.assertIsNone(url_data.url)
        self.assertFalse(url_data.should_ignore_warning("url-whitespace"))
