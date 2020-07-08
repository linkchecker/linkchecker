# Copyright (C) 2020 Chris Mayo
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
Test LocationInfo plugin.

Requires GeoIP (libgeoip-dev to build) and geoip-database
"""

import unittest

from linkcheck.plugins import locationinfo
from tests import need_geoip


class TestLocationInfo(unittest.TestCase):
    @need_geoip
    def test_get_location(self):
        location = locationinfo.get_location("8.8.8.8")
        self.assertEqual(location, "United States")
