# Copyright (C) 2022 Chris Mayo
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

from pathlib import Path
import shutil
import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

try:
    import polib
except ImportError:
    COMPILE_TRANSLATIONS = False
else:
    COMPILE_TRANSLATIONS = True

LOCALE_DIR = ("linkcheck", "data", "locale")
RELEASE_PY = ("linkcheck", "_release.py")


class CustomBuildHook(BuildHookInterface):
    def clean(self, versions):
        Path(*RELEASE_PY).unlink(missing_ok=True)
        shutil.rmtree(str(Path(*LOCALE_DIR)), ignore_errors=True)

    def initialize(self, version, build_data):
        cp = None
        committer_date = "unknown"
        try:
            cp = subprocess.run(["git", "log", "-n 1", "HEAD", "--format=%cs"],
                                capture_output=True, text=True)
        except FileNotFoundError:
            pass
        else:
            if cp and cp.stdout:
                committer_date = cp.stdout.strip()

        Path(*RELEASE_PY).write_text(
            f"__release_date__ = \"{committer_date}\"\n")

        if COMPILE_TRANSLATIONS:
            for po in Path("po").glob("*.po"):
                mo = Path(
                          *LOCALE_DIR,
                          po.stem, "LC_MESSAGES", "linkchecker",
                         ).with_suffix(".mo")
                pofile = polib.pofile(str(po))
                mo.parent.mkdir(exist_ok=True, parents=True)
                pofile.save_as_mofile(str(mo))
        else:
            self.app.display_warning(
                "polib package not found: translations not compiled")
