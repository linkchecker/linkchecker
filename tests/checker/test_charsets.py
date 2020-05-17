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
Test html <base> tag parsing.
"""
from . import LinkCheckTest


class TestBase(LinkCheckTest):
    """
    Test, if charset encoding is done right.
    The linkchecker should translate the encoding
    from the original source and show it on the terminal
    in most readable form.
    Check the tested files with browser - the link text
    should look the same in all of them.
    """

    def test_utf8(self):
        self.file_test("charsets/utf8.html")

    def test_iso8859_2(self):
        self.file_test("charsets/iso8859-2.html")

    def test_cp1250(self):
        self.file_test("charsets/cp1250.html")
