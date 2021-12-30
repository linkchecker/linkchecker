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
- creation and installation of configuration files with installation data
- automatic generation of .mo locale files
- automatic permission setting on POSIX systems for installed files

Because of all the features, this script is nasty and big.
Change it very carefully.
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
from distutils.command.install_lib import install_lib
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.install_data import install_data
from setuptools.command.sdist import sdist
from distutils.dir_util import remove_tree
from distutils.file_util import write_file
from distutils import util, log
from distutils.core import Distribution

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


def normpath(path):
    """Norm a path name to platform specific notation."""
    return os.path.normpath(path)


def cnormpath(path):
    """Norm a path name to platform specific notation and make it absolute."""
    path = normpath(path)
    if os.name == "nt":
        # replace slashes with backslashes
        path = path.replace("/", "\\")
    if not os.path.isabs(path):
        path = normpath(os.path.join(sys.prefix, path))
    return path


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
            for (src, bld_path, dst) in list_translation_files():
                pofile = polib.pofile(src)
                bld_path.parent.mkdir(exist_ok=True, parents=True)
                pofile.save_as_mofile(str(bld_path))
        super().run()


class MyInstallLib(install_lib):
    """Custom library installation."""

    def install(self):
        """Install the generated config file."""
        outs = super().install()
        infile = self.create_conf_file()
        outfile = os.path.join(self.install_dir, os.path.basename(infile))
        self.copy_file(infile, outfile)
        outs.append(outfile)
        return outs

    def create_conf_file(self):
        """Create configuration file."""
        cmd_obj = self.distribution.get_command_obj("install")
        cmd_obj.ensure_finalized()
        # we have to write a configuration file because we need the
        # <install_data> directory
        # all paths are made absolute by cnormpath()
        data = []
        for d in ["purelib", "platlib", "lib", "headers", "scripts", "data"]:
            attr = "install_%s" % d
            if cmd_obj.root:
                # cut off root path prefix
                cutoff = len(cmd_obj.root)
                # don't strip the path separator
                if cmd_obj.root.endswith(os.sep):
                    cutoff -= 1
                val = getattr(cmd_obj, attr)[cutoff:]
            else:
                val = getattr(cmd_obj, attr)
            if attr == "install_lib":
                if cmd_obj.root:
                    _drive, tail = os.path.splitdrive(val)
                    if tail.startswith(os.sep):
                        tail = tail[1:]
                    self.install_lib = os.path.join(cmd_obj.root, tail)
                else:
                    self.install_lib = val
            data.append("%s = %r" % (attr, cnormpath(val)))
        self.distribution.create_conf_file(data, directory=self.install_lib)
        return self.get_conf_output()

    def get_conf_output(self):
        """Get name of configuration file."""
        return self.distribution.get_conf_filename(self.install_lib)

    def get_outputs(self):
        """Add the generated config file to the list of outputs."""
        outs = super().get_outputs()
        conf_output = self.get_conf_output()
        outs.append(conf_output)
        if self.compile:
            outs.extend(self._bytecode_filenames([conf_output]))
        return outs


class MyInstallData(install_data):
    """Fix file permissions."""

    def run(self):
        """Handle translation files and adjust permissions on POSIX systems."""
        if COMPILE_TRANSLATIONS:
            for (src, bld_path, dst) in list_translation_files():
                self.data_files.append((dst, [str(bld_path)]))
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


class MyDistribution(Distribution):
    """Custom distribution class generating config file."""

    def run_commands(self):
        """Generate config file and run commands."""
        cwd = os.getcwd()
        data = []
        data.append("install_data = %r" % cwd)
        self.create_conf_file(data)
        super().run_commands()

    def get_conf_filename(self, directory):
        """Get name for config file."""
        return os.path.join(directory, "_%s_configdata.py" % self.get_name())

    def create_conf_file(self, data, directory=None):
        """Create local config file from given data (list of lines) in
        the directory (or current directory if not given)."""
        data.insert(0, "# this file is automatically created by setup.py")
        data.insert(0, "# -*- coding: iso-8859-1 -*-")
        if directory is None:
            directory = os.getcwd()
        filename = self.get_conf_filename(directory)
        # add metadata
        data.append('release_date = "%s"' % get_release_date())
        # write the config file
        util.execute(
            write_file,
            (filename, data),
            "creating %s" % filename,
            self.verbose >= 1,
            self.dry_run,
        )


def list_translation_files():
    """Return list of translation files and their build and installation paths."""
    for po in Path("po").glob("*.po"):
        mo = Path(
            "share", "locale", po.stem, "LC_MESSAGES", AppName.lower()
            ).with_suffix(".mo")
        build_mo = Path("build", mo)
        build_mo.parent.mkdir(exist_ok=True, parents=True)
        yield (str(po), build_mo, str(mo.parent))


class MyClean(clean):
    """Custom clean command."""

    def run(self):
        """Remove share directory on clean."""
        if self.all:
            # remove share directory
            directory = os.path.join("build", "share")
            if os.path.exists(directory):
                remove_tree(directory, dry_run=self.dry_run)
            else:
                log.warn("'%s' does not exist -- can't clean it", directory)
        clean.run(self)


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
    distclass=MyDistribution,
    cmdclass={
        "sdist": MySdist,
        "build": MyBuild,
        "install_lib": MyInstallLib,
        "install_data": MyInstallData,
        "clean": MyClean,
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
