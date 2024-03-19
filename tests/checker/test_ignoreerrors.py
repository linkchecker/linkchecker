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
Test ignoring of errors.
"""

from re import compile as re_compile

from tests import need_network
from . import LinkCheckTest


class TestIgnoreErrors(LinkCheckTest):
    """
    Test whether ignoring of errors per URL works.
    """

    def _test(self, url, url_regex, msg_regex, valid):
        """ Shorthand for various tests of ignoring errors. """
        confargs = {
            "ignoreerrors": [
                (re_compile(url_regex), re_compile(msg_regex))
            ]
        }
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid" if valid else "error",
        ]
        self.direct(url, resultlines, confargs=confargs)

    @need_network
    def test_no_error(self):
        """ Test that unmatched errors are not ignored. """
        self._test("mailto:good@example.com", "", "", True)
        self._test("mailto:good@example.com", "^$", "", True)
        self._test("mailto:good@example.com", "^$", "^no-match$", True)
        self._test("mailto:good@example.com",
                   r"^mailto:good@example\.com$", "", True)
        self._test("mailto:good@example.com",
                   r"^mailto:good@example\.com$", "^$", True)

    def test_url_regex(self):
        """ Test that URLs are properly matched. """
        self._test("mailto:foo", r"^$", "", False)
        self._test("mailto:foo", r"", "", True)
        self._test("mailto:foo", r"^mailto:foo$", "", True)
        self._test("mailto:foobar", r"^mailto:foo", "", True)

    def test_msg_regex(self):
        """ Test that error messages are properly matched. """
        self._test("mailto:foo", r"^mailto:foo$", "^$", False)
        self._test("mailto:foo", r"^mailto:foo$", "", True)
        self._test("mailto:foo", r"^mailto:foo$",
                   r"^Missing `@' in mail address `foo'.$", True)

    @need_network
    def test_internet(self):
        """ Test a few well-known Internet URLs. """
        self._test("https://linkchecker.github.io/does-not-exist",
                   r"^https://linkchecker.github.io/.+$", "^404", True)
        self._test("http://does-not-exist.example.com",
                   r"example.com", "^ConnectionError", True)
