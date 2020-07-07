# -*- coding: iso-8859-1 -*-
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
Test string formatting operations.
"""

import unittest
import os
import time
import linkcheck.strformat


class TestStrFormat(unittest.TestCase):
    """
    Test string formatting routines.
    """

    def test_unquote(self):
        # Test quote stripping.
        u = linkcheck.strformat.unquote
        self.assertEqual(u(""), "")
        self.assertEqual(u(None), None)
        self.assertEqual(u("'"), "'")
        self.assertEqual(u('"'), '"')
        self.assertEqual(u('""'), "")
        self.assertEqual(u("''"), "")
        self.assertEqual(u("'a'"), "a")
        self.assertEqual(u("'a\"'"), 'a"')
        self.assertEqual(u("'\"a'"), '"a')
        self.assertEqual(u('"a\'"'), "a'")
        self.assertEqual(u('"\'a"'), "'a")
        self.assertEqual(u("'a'", matching=True), "a")
        self.assertEqual(u('"a"', matching=True), "a")
        # even mis-matching quotes should be removed...
        self.assertEqual(u("'a\""), "a")
        self.assertEqual(u("\"a'"), "a")
        # ...but not when matching is True
        self.assertEqual(u("'a\"", matching=True), "'a\"")
        self.assertEqual(u("\"a'", matching=True), "\"a'")

    def test_wrap(self):
        # Test line wrapping.
        wrap = linkcheck.strformat.wrap
        s = "11%(sep)s22%(sep)s33%(sep)s44%(sep)s55" % {"sep": os.linesep}
        # testing width <= 0
        self.assertEqual(wrap(s, -1), s)
        self.assertEqual(wrap(s, 0), s)
        n = len(os.linesep)
        gap = " "
        s2 = "11%(gap)s22%(sep)s33%(gap)s44%(sep)s55" % {"sep": os.linesep, "gap": gap}
        # splitting lines
        self.assertEqual(wrap(s2, 2), s)
        # combining lines
        self.assertEqual(wrap(s, 4 + n), s2)
        # misc
        self.assertEqual(wrap(s, -1), s)
        self.assertEqual(wrap(s, 0), s)
        self.assertEqual(wrap(None, 10), None)
        self.assertFalse(linkcheck.strformat.get_paragraphs(None))

    def test_strsize(self):
        # Test byte size strings.
        self.assertRaises(ValueError, linkcheck.strformat.strsize, -1)
        self.assertEqual(linkcheck.strformat.strsize(0), "0B")
        self.assertEqual(linkcheck.strformat.strsize(1), "1B")
        self.assertEqual(linkcheck.strformat.strsize(2), "2B")
        self.assertEqual(linkcheck.strformat.strsize(1023, grouping=False), "1023B")
        self.assertEqual(linkcheck.strformat.strsize(1024), "1KB")
        self.assertEqual(linkcheck.strformat.strsize(1024 * 25), "25.00KB")
        self.assertEqual(linkcheck.strformat.strsize(1024 * 1024), "1.00MB")
        self.assertEqual(linkcheck.strformat.strsize(1024 * 1024 * 11), "11.0MB")
        self.assertEqual(linkcheck.strformat.strsize(1024 * 1024 * 1024), "1.00GB")
        self.assertEqual(linkcheck.strformat.strsize(1024 * 1024 * 1024 * 14), "14.0GB")

    def test_indent(self):
        s = "bla"
        self.assertEqual(linkcheck.strformat.indent(s, ""), s)
        self.assertEqual(linkcheck.strformat.indent(s, " "), " " + s)

    def test_stripurl(self):
        self.assertEqual(linkcheck.strformat.stripurl("a\tb"), "a\tb")
        self.assertEqual(linkcheck.strformat.stripurl(" a\t b"), "a\t b")
        self.assertEqual(linkcheck.strformat.stripurl(" ab\t\ra\nb"), "ab")
        self.assertEqual(linkcheck.strformat.stripurl(None), None)
        self.assertEqual(linkcheck.strformat.stripurl(""), "")

    def test_limit(self):
        self.assertEqual(linkcheck.strformat.limit("", 0), "")
        self.assertEqual(linkcheck.strformat.limit("a", 0), "")
        self.assertEqual(linkcheck.strformat.limit("1", 1), "1")
        self.assertEqual(linkcheck.strformat.limit("11", 1), "1...")

    def test_strtime(self):
        zone = linkcheck.strformat.strtimezone()
        t = linkcheck.strformat.strtime(0, func=time.gmtime)
        self.assertEqual(t, "1970-01-01 00:00:00" + zone)

    def test_duration_long(self):
        def duration(s):
            return linkcheck.strformat.strduration_long(s, do_translate=False)
        self.assertEqual(duration(-0.5), "-0.50 seconds")
        self.assertEqual(duration(0), "0.00 seconds")
        self.assertEqual(duration(0.9), "0.90 seconds")
        self.assertEqual(duration(1), "1 second")
        self.assertEqual(duration(2), "2 seconds")
        self.assertEqual(duration(60), "1 minute")
        self.assertEqual(duration(120), "2 minutes")
        self.assertEqual(duration(60 * 60), "1 hour")
        self.assertEqual(duration(60 * 60 * 24), "1 day")
        self.assertEqual(duration(60 * 60 * 24 * 365), "1 year")
        self.assertEqual(
            duration(60 * 60 * 24 * 365 + 60 * 60 * 24 + 2), "1 year, 1 day"
        )

    def test_ascii_safe(self):
        ascii_safe = linkcheck.strformat.ascii_safe
        self.assertEqual(ascii_safe("a"), "a")
        self.assertEqual(ascii_safe("ä"), "")

    def test_strip_control_chars(self):
        strip = linkcheck.strformat.strip_control_chars
        self.assertEqual(strip(""), "")
        self.assertEqual(strip("a"), "a")
        self.assertEqual(strip("ä"), "ä")
        self.assertEqual(strip("\x01"), "")
