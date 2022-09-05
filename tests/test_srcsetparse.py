# Copyright (C) 2022 Stefan fisk
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
Test srcset attribute parsing.
"""

import unittest
from linkcheck.htmlutil.srcsetparse import parse_srcset

from parameterized import parameterized


# list of tuples
# (<input>, <expected parsed URLs>)
parsetests = [
    ('', []),
    ('   ', []),
    (',', []),
    ('\t\n ,,\t\n,,   \t\n', []),
    ('foo', ['foo']),
    ('foo,bar, ,foo, bar', ['foo,bar', 'foo', 'bar']),
    ('https://example.com/1 foo, https://example.com/2 bar',
        ['https://example.com/1', 'https://example.com/2']),
    ('   foo   ', ['foo']),
    (',,,foo,,,', ['foo']),
    (',foo,bar,baz,', ['foo,bar,baz']),
    ('foo bar baz', ['foo']),
    ('foo, bar baz', ['foo', 'bar']),
    ('foo/1 bar, foo/2', ['foo/1', 'foo/2']),
    ('foo/1 (foo/2)', ['foo/1']),
    ('foo/1 (((, foo/2', ['foo/1']),
]


class TestSrcsetParsing(unittest.TestCase):
    @parameterized.expand(parsetests)
    def test_parse(self, _in, _urls):
        self.assertEqual(parse_srcset(_in), _urls)
