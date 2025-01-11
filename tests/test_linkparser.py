# Copyright (C) 2005-2014 Bastian Kleineidam
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
Test linkparser routines.
"""

from linkcheck.htmlutil import htmlsoup, linkparse

from . import TestBase


class TestLinkparser(TestBase):
    """
    Test link parsing.
    """

    def _test_one_link(self, content, url):
        self.count_url = 0
        linkparse.find_links(
            htmlsoup.make_soup(content), self._test_one_url(url), linkparse.LinkTags
        )
        self.assertEqual(self.count_url, 1)

    def _test_one_url(self, origurl):
        """Return parser callback function."""

        def callback(url, line, column, name, base):
            self.count_url += 1
            self.assertEqual(origurl, url)

        return callback

    def _test_no_link(self, content):
        def callback(url, line, column, name, base):
            self.assertTrue(False, "URL %r found" % url)

        linkparse.find_links(htmlsoup.make_soup(content), callback, linkparse.LinkTags)

    def test_href_parsing(self):
        # Test <a href> parsing.
        content = '<a href="%s">'
        url = "alink"
        self._test_one_link(content % url, url)
        url = " alink"
        self._test_one_link(content % url, url)
        url = "alink "
        self._test_one_link(content % url, url)
        url = " alink "
        self._test_one_link(content % url, url)

    def test_rel_parsing(self):
        # Test <link rel> parsing.
        content = '<link rel="%s" href="%s">'
        rel = "dns-prefetch"
        url = "https://alink"
        expected = "dns://alink"
        self._test_one_link(content % (rel, url), expected)
        url = "//alink/"
        self._test_one_link(content % (rel, url), expected)
        rel = "preconnect"
        url = "https://alink"
        self._test_one_link(content % (rel, url), expected)
        rel = "dns-prefetch preconnect"
        url = "https://alink"
        self._test_one_link(content % (rel, url), expected)

    def test_link_without_rel_parsing(self):
        # <link> tags without rel attr should not raise TypeError.
        content = '<link href="%s">'
        url = "https://alink"
        expected = "https://alink"
        # Dummy test, we just have to make sure no error was raised.
        self._test_one_link(content % url, expected)

    def test_img_srcset_parsing(self):
        content = '<img srcset="%s 1x">'
        url = "imagesmall.jpg"
        self._test_one_link(content % url, url)
        content = '<img srcset="imagesmall.jpg 1x,">'
        url = "imagesmall.jpg"
        self._test_one_link(content, url)
        content = '<img srcset="data:image/vnd.microsoft.icon,000001000200">'
        url = "data:image/vnd.microsoft.icon,000001000200"
        self._test_one_link(content, url)

    def test_source_srcset_parsing(self):
        content = '<source srcset="%s 1x">'
        url = "imagesmall.jpg"
        self._test_one_link(content % url, url)
        content = '<source srcset="imagesmall.jpg 1x,">'
        url = "imagesmall.jpg"
        self._test_one_link(content, url)
        content = '<source srcset="data:image/vnd.microsoft.icon,000001000200">'
        url = "data:image/vnd.microsoft.icon,000001000200"
        self._test_one_link(content, url)

    def test_itemtype_parsing(self):
        content = '<div itemtype="%s">'
        url = "http://example.org/Movie"
        self._test_one_link(content % url, url)

    def test_form_parsing(self):
        # Test <form action> parsing
        content = '<form action="%s">'
        url = "alink"
        self._test_one_link(content % url, url)
        content = '<form action="%s" method="POST">'
        url = "alink"
        self._test_no_link(content % url)

    def test_css_parsing(self):
        # Test css style attribute parsing.
        content = '<table style="background: url(%s) no-repeat" >'
        url = "alink"
        self._test_one_link(content % url, url)
        content = '<table style="background: url(%s) no-repeat" >'
        self._test_one_link(content % url, url)
        content = '<table style="background: url(%s ) no-repeat" >'
        self._test_one_link(content % url, url)
        content = '<table style="background: url( %s ) no-repeat" >'
        self._test_one_link(content % url, url)
        content = "<table style=\"background: url('%s') no-repeat\" >"
        self._test_one_link(content % url, url)
        content = "<table style='background: url(\"%s\") no-repeat' >"
        self._test_one_link(content % url, url)
        content = "<table style=\"background: url('%s' ) no-repeat\" >"
        self._test_one_link(content % url, url)
        content = "<table style='background: url( \"%s\") no-repeat' >"
        self._test_one_link(content % url, url)

    def test_comment_stripping(self):
        strip = linkparse.strip_c_comments
        content = "/* url('http://example.org')*/"
        self.assertEqual(strip(content), "")
        content = "/* * * **/"
        self.assertEqual(strip(content), "")
        content = "/* * /* * **//* */"
        self.assertEqual(strip(content), "")
        content = "a/* */b/* */c"
        self.assertEqual(strip(content), "abc")

    def test_url_quoting(self):
        url = "http://example.com/bla/a=b"
        content = '<a href="%s&quot;">'
        self._test_one_link(content % url, url + '"')
