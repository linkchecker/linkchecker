# Copyright (C) 2021 Chris Mayo
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
Test guess_url.
"""

import unittest
from linkcheck.checker import guess_url


class TestGuestUrl(unittest.TestCase):
    """
    Test guess_url.
    """

    def test_guess_url(self):
        url = "www.example.com"
        self.assertEqual(guess_url(url), f"http://{url}")
        url = "ftp.example.com"
        self.assertEqual(guess_url(url), f"ftp://{url}")
        url = "ftp.html"
        self.assertEqual(guess_url(url), url)
        url = "www.html"
        self.assertEqual(guess_url(url), url)
