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
from . import LinkCheckTest
from . import TestLogger
from .. import has_windows


class AllPartsLogger(TestLogger):
    logparts = [
        "cachekey",
        "realurl",
        "name",
        "base",
        "info",
        "warning",
        "result",
        "url",
        "line",
        "col",
        "size",
        "parent_url",
        "page",
        "content_type",
    ]


class TestAllParts(LinkCheckTest):
    """
    Test that all parts of logger are working properly.
    """

    logger = AllPartsLogger

    def test_all_parts_linenos(self):
        if has_windows():
            self.file_test("all_parts_linenos_windows.html")
        else:
            self.file_test("all_parts_linenos.html")
