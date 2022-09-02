# Copyright (C) 2006-2014 Bastian Kleineidam
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
Test virus filter.
"""
import unittest
from tests import need_clamav
from linkcheck.plugins import viruscheck as clamav


class TestClamav(unittest.TestCase):
    def setUp(self):
        self.clamav_conf = clamav.get_clamav_conf("/etc/clamav/clamd.conf")

    @need_clamav
    def testClean(self):
        data = b""
        infected, errors = clamav.scan(data, self.clamav_conf)
        self.assertFalse(infected)
        self.assertFalse(errors)

    @need_clamav
    def testInfected(self):
        # from the clamav test directory: the clamav test file as html data
        data = (
            b'<a href="data:application/octet-stream;base64,'
            b"TVpQAAIAAAAEAA8A//8AALgAAAAhAAAAQAAaAAAAAAAAAAAAAAAAAAAAAAAAAA"
            b"AAAAAAAAAAAAAAAAAAAAEAALtxEEAAM8BQUIvzU1NQsClAMARmrHn5ujEAeA2t"
            b"UP9mcA4fvjEA6eX/tAnNIbRMzSFiDAoBAnB2FwIeTgwEL9rMEAAAAAAAAAAAAA"
            b"AAAAAAwBAAAIAQAAAAAAAAAAAAAAAAAADaEAAA9BAAAAAAAAAAAAAAAAAAAAAA"
            b"AAAAAAAAS0VSTkVMMzIuRExMAABFeGl0UHJvY2VzcwBVU0VSMzIuRExMAENMQU"
            b"1lc3NhZ2VCb3hBAOYQAAAAAAAAPz8/P1BFAABMAQEAYUNhQgAAAAAAAAAA4ACO"
            b"gQsBAhkABAAAAAYAAAAAAABAEAAAABAAAEAAAAAAAEAAABAAAAACAAABAAAAAA"
            b"AAAAMACgAAAAAAACAAAAAEAAAAAAAAAgAAAAAAEAAAIAAAAAAQAAAQAAAAAAAA"
            b"EAAAAAAAAAAAAAAAhBAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            b"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW0NMQU1BVl"
            b'0AEAAAABAAAAACAAABAAAAAAAAAAAAAAAAAAAAAAAAwA==">t</a>'
        )
        infected, errors = clamav.scan(data, self.clamav_conf)
        # different versions of clamav report different responses, apparently
        acceptable_responses = (
            [
              "stream: ClamAV-Test-File(2d1206194bd704385e37000be6113f73:781) FOUND\n"
            ],
            [
              "stream: Clamav.Test.File-6(aa15bcf478d165efd2065190eb473bcb:544) FOUND\n"
            ],
            [
              "stream: Clamav.Test.File-6(2d1206194bd704385e37000be6113f73:781) FOUND\n"
            ],
        )
        self.assertIn(infected, acceptable_responses)
        self.assertFalse(errors)
