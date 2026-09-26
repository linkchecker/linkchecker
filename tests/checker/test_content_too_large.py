# Copyright (C) 2024 LinkChecker Authors
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
Test the warning tag used when content exceeds maxfilesizedownload.
"""
from unittest import mock

from linkcheck.checker.const import WARN_URL_CONTENT_SIZE_TOO_LARGE
from linkcheck.checker.urlbase import UrlBase
from .. import TestBase


class TestContentTooLarge(TestBase):
    """
    Exceeding maxfilesizedownload is not an error getting the content,
    so it must be tagged url-content-too-large and therefore be
    ignorable with ignorewarnings.
    """

    def get_url_data(self, maxfilesizedownload):
        url_data = UrlBase.__new__(UrlBase)
        url_data.do_check_content = True
        url_data.valid = True
        url_data.warnings = []
        url_data.info = []
        url_data.size = 0
        url_data.dltime = 0
        url_data.data = None
        url_data.caching = True
        url_data.url = "http://example.org/huge.html"
        url_data.aggregate = mock.Mock()
        url_data.aggregate.config = {
            "maxfilesizedownload": maxfilesizedownload,
        }
        url_data.should_ignore_warning = lambda tag: False
        url_data.can_get_content = lambda: True
        url_data.allows_recursion = lambda: False
        url_data.url_connection = mock.Mock()
        url_data.url_connection.read.side_effect = [b"x" * 100, b""]
        url_data.aggregate.plugin_manager.run_content_plugins.side_effect = (
            lambda url_data: url_data.get_raw_content()
        )
        return url_data

    def test_too_large_content_warning_tag(self):
        url_data = self.get_url_data(5)
        self.assertFalse(url_data.check_content())
        self.assertEqual(len(url_data.warnings), 1)
        self.assertEqual(url_data.warnings[0][0], WARN_URL_CONTENT_SIZE_TOO_LARGE)
