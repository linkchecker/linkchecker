# Copyright (C) 2005 Joe Wreschnig
# Copyright (C) 2005-2010 Bastian Kleineidam
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
Test gettext .po files.
"""

import unittest
import subprocess
import glob
from tests import need_msgfmt, need_posix


pofiles = None


def get_pofiles():
    """Find all .po files in this source."""
    global pofiles
    if pofiles is None:
        pofiles = []
        pofiles.extend(glob.glob("po/*.po"))
        pofiles.extend(glob.glob("doc/i18n/locales/**/*.po", recursive=True))
    if not pofiles:
        raise Exception("No .po files found")
    return pofiles


class TestPo(unittest.TestCase):
    """Test .po file syntax."""

    @need_posix
    @need_msgfmt
    def test_pos(self):
        """Test .po files syntax."""
        for f in get_pofiles():
            cp = subprocess.run(["msgfmt", "-c", "-o", "-", f], capture_output=True)
            self.assertEqual(
                cp.returncode, 0,
                msg=f"PO-file syntax error in {f!r}: {str(cp.stderr, 'utf-8')}")


class TestGTranslator(unittest.TestCase):
    """GTranslator displays a middot · for a space. Unfortunately, it
    gets copied with copy-and-paste, what a shame."""

    def test_gtranslator(self):
        """Test all pofiles for GTranslator brokenness."""
        for f in get_pofiles():
            with open(f, encoding="UTF-8") as fd:
                self.check_file(fd, f)

    def check_file(self, fd, f):
        """Test for GTranslator broken syntax."""
        for line in fd:
            if line.strip().startswith("#"):
                continue
            self.assertFalse(
                "·" in line,
                f"Broken GTranslator copy/paste in {f!r}:\n{line}",
            )
