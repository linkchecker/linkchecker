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
Test file parsing.
"""
import os
from pathlib import Path
import sys
import zipfile

import pytest

from tests import need_network, need_word, need_pdflib
from . import LinkCheckTest, get_file


def unzip(filename, targetdir):
    """Unzip given zipfile into targetdir."""
    # There are likely problems with zipfile and non-Unicode filenames
    # https://github.com/python/cpython/issues/83042
    # https://github.com/python/cpython/issues/72267
    # https://github.com/python/cpython/issues/95463
    zf = zipfile.ZipFile(filename)
    for name in zf.namelist():
        if name.endswith("/"):
            os.mkdir(os.path.join(targetdir, name), 0o700)
        else:
            outfile = open(os.path.join(targetdir, name), "wb")
            try:
                outfile.write(zf.read(name))
            finally:
                outfile.close()


class TestFile(LinkCheckTest):
    """
    Test file:// link checking (and file content parsing).
    """

    def test_html(self):
        self.file_test("file.html")

    @need_network
    def test_html_url_quote(self):
        self.file_test("file_url_quote.html")

    def test_wml(self):
        self.file_test("file.wml")

    def test_text(self):
        self.file_test("file.txt")

    def test_asc(self):
        self.file_test("file.asc")

    def test_css(self):
        self.file_test("file.css")

    def test_php(self):
        self.file_test("file.php")

    def test_empty(self):
        self.file_test("empty.html")

    @need_word
    def test_word(self):
        confargs = dict(enabledplugins=["WordParser"])
        self.file_test("file.doc", confargs=confargs)

    @need_pdflib
    def test_pdf(self):
        confargs = dict(enabledplugins=["PdfParser"])
        self.file_test("file.pdf", confargs=confargs)

    def test_markdown(self):
        confargs = dict(enabledplugins=["MarkdownCheck"])
        self.file_test("file.markdown", confargs=confargs)

    def test_urllist(self):
        self.file_test("urllist.txt")

    @pytest.mark.xfail(strict=True)
    def test_directory_listing(self):
        # unpack non-unicode filename which cannot be stored
        # in the SF subversion repository
        if os.name != "posix" or sys.platform != "linux":
            pytest.skip("Not running on POSIX or Linux")
        dirname = get_file("dir")
        if not os.path.isdir(dirname):
            unzip(dirname + ".zip", os.path.dirname(dirname))
        self.file_test("dir")

    def test_directory_listing_unicode(self):
        if os.name != "posix" or sys.platform != "linux":
            pytest.skip("Not running on POSIX or Linux")
        dirname = Path(get_file("udir"))
        dirname.mkdir(exist_ok=True)
        Path(dirname, "í»­¯¿.dat").touch()
        self.file_test("udir")

    def test_unicode_filename(self):
        # a unicode filename
        self.file_test("Мошкова.bin")

    def test_good_file(self):
        url = "file://%(curdir)s/%(datadir)s/file.txt" % self.get_attrs()
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "valid",
        ]
        self.direct(url, resultlines)

    def test_bad_file(self):
        if os.name == "nt":
            # Fails on NT platforms and I am too lazy to fix
            # Cause: url get quoted %7C which gets lowercased to
            # %7c and this fails.
            pytest.skip("Not running on NT")
        url = "file:/%(curdir)s/%(datadir)s/file.txt" % self.get_attrs()
        nurl = self.norm(url)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "error",
        ]
        self.direct(url, resultlines)

    def test_good_file_missing_dslash(self):
        # good file (missing double slash)
        attrs = self.get_attrs()
        url = "file:%(curdir)s/%(datadir)s/file.txt" % attrs
        resultlines = [
            "url %s" % url,
            "cache key file://%(curdir)s/%(datadir)s/file.txt" % attrs,
            "real url file://%(curdir)s/%(datadir)s/file.txt" % attrs,
            "valid",
        ]
        self.direct(url, resultlines)

    def test_good_dir(self):
        url = "file://%(curdir)s/%(datadir)s/" % self.get_attrs()
        resultlines = [
            "url %s" % url,
            "cache key %s" % url,
            "real url %s" % url,
            "valid",
        ]
        self.direct(url, resultlines)

    def test_good_dir_space(self):
        url = "file://%(curdir)s/%(datadir)s/a b/" % self.get_attrs()
        nurl = self.norm(url)
        url2 = "file://%(curdir)s/%(datadir)s/a b/el.html" % self.get_attrs()
        nurl2 = self.norm(url2)
        url3 = "file://%(curdir)s/%(datadir)s/a b/t.txt" % self.get_attrs()
        nurl3 = self.norm(url3)
        resultlines = [
            "url %s" % url,
            "cache key %s" % nurl,
            "real url %s" % nurl,
            "valid",
            "url el.html",
            "cache key %s" % nurl2,
            "real url %s" % nurl2,
            "name el.html",
            "valid",
            "url t.txt",
            "cache key %s" % nurl3,
            "real url %s" % nurl3,
            "name t.txt",
            "valid",
        ]
        self.direct(url, resultlines, recursionlevel=2)
