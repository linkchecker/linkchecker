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

from tests import need_network
from . import LinkCheckTest


class TestWarnings(LinkCheckTest):
    """
    Test whether ignoring of warnings per URL works.
    """

    def test_ignorewarnings_for_specified_url_and_warning(self):
        confargs = {
            "ignorewarningsforurls": [
                (re_compile("test.txt"), re_compile("url-content-size-zero"))
            ]
        }
        self.file_test("base_ignorewarnings.html", confargs=confargs)

    def test_ignorewarnings_for_incorrect_url(self):
        confargs = {
            "ignorewarningsforurls": [
                (re_compile("test_incorrect.txt"), re_compile("url-content-size-zero"))
            ]
        }
        self.file_test("base_ignorewarnings_with_warning.html", confargs=confargs)

    def test_ignorewarnings_for_incorrect_warning(self):
        confargs = {
            "ignorewarningsforurls": [
                (re_compile("test.txt"), re_compile("not-a-warning"))
            ]
        }
        self.file_test("base_ignorewarnings_with_warning.html", confargs=confargs)

