#!/usr/bin/python3
# Copyright (C) 2000-2014 Bastian Kleineidam
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
Setup file for the distuils module.

It includes the following features:
- records the release date
- automatic generation of .mo locale files
- automatic permission setting on POSIX systems for installed files
"""
import sys

if sys.version_info < (3, 7, 0, "final", 0):
    raise SystemExit("This program requires Python 3.7 or later.")
import os
import stat
import subprocess
from pathlib import Path

# import Distutils stuff
from setuptools import find_packages, setup
from distutils.command.build import build
from distutils.command.install_data import install_data
from setuptools.command.egg_info import egg_info
from setuptools.command.sdist import sdist

try:
    import polib
except ImportError:
    print("polib package not found. Translations not compiled.")
    COMPILE_TRANSLATIONS = False
else:
    COMPILE_TRANSLATIONS = True

# the application name
AppName = "LinkChecker"
Description = "check links in web documents or full websites"

RELEASE_DATE_FILE = "_release_date"


def get_long_description():
    """Try to read long description from README.rst."""
    try:
        with open("README.rst") as f:
            return f.read()
    except Exception:
        return Description


def get_release_date(for_sdist=False):
    """Return release date as a string from the most recent commit."""
    release_date = "unknown"
    cp = None
    try:
        # need git >= 2.25.0 for %cs
        cp = subprocess.run(["git", "log", "-n 1", "HEAD", "--format=%cI"],
                            capture_output=True, text=True)
    except FileNotFoundError:
        pass
    if cp and cp.stdout:
        release_date = cp.stdout.split("T")[0]
    elif not for_sdist:
        try:
            release_date = Path(RELEASE_DATE_FILE).read_text()
        except FileNotFoundError:
            pass
    return release_date


class MySdist(sdist):
    def run(self):
        Path(RELEASE_DATE_FILE).write_text(get_release_date(for_sdist=True))
        super().run()


class MyBuild(build):
    """Custom build with translation compilation"""

    def run(self):
        if COMPILE_TRANSLATIONS:
            for po in Path("po").glob("*.po"):
                mo = Path(
                          self.build_lib, "linkcheck", "data", "locale",
                          po.stem, "LC_MESSAGES", AppName.lower()
                         ).with_suffix(".mo")
                pofile = polib.pofile(str(po))
                mo.parent.mkdir(exist_ok=True, parents=True)
                pofile.save_as_mofile(str(mo))
        super().run()


class MyEggInfo(egg_info):
    def run(self):
        """Add release date to metadata."""
        super().run()
        self.write_file(
            "release date",
            os.path.join(self.egg_info, "RELEASE_DATE"),
            get_release_date()
        )


class MyInstallData(install_data):
    """Fix file permissions."""

    def run(self):
        """Adjust permissions on POSIX systems."""
        super().run()
        self.fix_permissions()

    def fix_permissions(self):
        """Set correct read permissions on POSIX systems. Might also
        be possible by setting umask?"""
        if os.name == "posix" and not self.dry_run:
            # Make the data files we just installed world-readable,
            # and the directories world-executable as well.
            for path in self.get_outputs():
                mode = os.stat(path)[stat.ST_MODE]
                if stat.S_ISDIR(mode):
                    mode |= 0o11
                mode |= 0o44
                os.chmod(path, mode)


# scripts
myname = "LinkChecker Authors"
myemail = ""

data_files = [
    (
        "share/linkchecker/examples",
        [
            "cgi-bin/lconline/leer.html.en",
            "cgi-bin/lconline/leer.html.de",
            "cgi-bin/lconline/index.html",
            "cgi-bin/lconline/lc_cgi.html.en",
            "cgi-bin/lconline/lc_cgi.html.de",
            "cgi-bin/lconline/check.js",
            "cgi-bin/lc.wsgi",
            "config/linkchecker.apache2.conf",
        ],
    ),
]

if os.name == "posix":
    data_files.append(("share/man/man1", ["doc/man/en/linkchecker.1"]))
    data_files.append(("share/man/man5", ["doc/man/en/linkcheckerrc.5"]))
    data_files.append(("share/man/de/man1", ["doc/man/de/linkchecker.1"]))
    data_files.append(("share/man/de/man5", ["doc/man/de/linkcheckerrc.5"]))
    data_files.append(
        (
            "share/linkchecker/examples",
            [
                "config/linkchecker-completion",
                "doc/examples/check_failures.sh",
                "doc/examples/check_for_x_errors.sh",
                "doc/examples/check_urls.sh",
            ],
        )
    )

setup(
    name=AppName,
    use_scm_version={
        "local_scheme": "node-and-timestamp",
        "version_scheme": "post-release",
    },
    description=Description,
    keywords="link,url,site,checking,crawling,verification,validation",
    author=myname,
    author_email=myemail,
    maintainer=myname,
    maintainer_email=myemail,
    url="https://linkchecker.github.io/linkchecker/",
    license="GPL",
    long_description=get_long_description(),
    long_description_content_type="text/x-rst",
    cmdclass={
        "sdist": MySdist,
        "build": MyBuild,
        "egg_info": MyEggInfo,
        "install_data": MyInstallData,
    },
    packages=find_packages(include=["linkcheck", "linkcheck.*"]),
    entry_points={
        "console_scripts": [
            "linkchecker = linkcheck.command.linkchecker:linkchecker"
        ]
    },
    data_files=data_files,
    include_package_data=True,
    classifiers=[
        "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    options={},
    # Requirements, usable with setuptools or the new Python packaging module.
    python_requires=">= 3.7",
    setup_requires=["setuptools_scm"],
    install_requires=[
        "importlib_metadata;python_version<'3.8'",
        "requests >= 2.4",
        "dnspython >= 2.0",
        "beautifulsoup4 >= 4.8.1",
        "pyxdg",
    ],
    # Commented out since they are untested and not officially supported.
    # See also doc/install.txt for more detailed dependency documentation.
    # extra_requires = {
    #    "IP country info": ['GeoIP'], # https://pypi.org/project/GeoIP/
    #    "Bash completion": ['argcomplete'], # https://pypi.org/project/argcomplete/
    #    "Memory debugging": ['meliae'], # https://pypi.org/project/meliae/
    # }
)
