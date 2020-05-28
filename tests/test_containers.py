# Copyright (C) 2004-2011 Bastian Kleineidam
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
Test container routines.
"""

import unittest

import linkcheck.containers


class TestLFUCache(unittest.TestCase):
    """Test LFU cache implementation."""

    def setUp(self):
        """Set up self.d as empty LFU cache with default size of 1000."""
        self.size = 1000
        self.d = linkcheck.containers.LFUCache(self.size)

    def test_num_uses(self):
        self.assertTrue(not self.d)
        self.d["a"] = 1
        self.assertTrue("a" in self.d)
        self.assertEqual(self.d.uses("a"), 0)
        dummy = self.d["a"]
        self.assertEqual(self.d.uses("a"), 1)
        del dummy

    def test_values(self):
        self.assertTrue(not self.d)
        self.d["a"] = 1
        self.d["b"] = 2
        self.assertEqual(set([1, 2]), set(self.d.values()))
        self.assertEqual(set([1, 2]), set(self.d.itervalues()))

    def test_popitem(self):
        self.assertTrue(not self.d)
        self.d["a"] = 42
        self.assertEqual(self.d.popitem(), ("a", 42))
        self.assertTrue(not self.d)
        self.assertRaises(KeyError, self.d.popitem)

    def test_shrink(self):
        self.assertTrue(not self.d)
        for i in range(self.size):
            self.d[i] = i
        self.d[1001] = 1001
        self.assertTrue(950 <= len(self.d) <= self.size)
