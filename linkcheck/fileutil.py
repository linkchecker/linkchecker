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
File and path utilities.
"""

import os
import locale
import stat
import tempfile
import importlib
from functools import lru_cache


def has_module(name, without_error=True):
    """Test if given module can be imported.
    @param without_error: True if module must not throw any errors when importing
    @return: flag if import is successful
    @rtype: bool
    """
    try:
        importlib.import_module(name)
        return True
    except ImportError:
        return False
    except Exception:
        # some modules raise errors when intitializing
        return not without_error


def get_mtime(filename):
    """Return modification time of filename or zero on errors."""
    try:
        return os.path.getmtime(filename)
    except os.error:
        return 0


def get_size(filename):
    """Return file size in Bytes, or -1 on error."""
    try:
        return os.path.getsize(filename)
    except os.error:
        return -1


# http://developer.gnome.org/doc/API/2.0/glib/glib-running.html
if "G_FILENAME_ENCODING" in os.environ:
    FSCODING = os.environ["G_FILENAME_ENCODING"].split(",")[0]
    if FSCODING == "@locale":
        FSCODING = locale.getpreferredencoding()
elif "G_BROKEN_FILENAMES" in os.environ:
    FSCODING = locale.getpreferredencoding()
else:
    FSCODING = "utf-8"


def path_safe(path):
    """Ensure path string is compatible with the platform file system encoding."""
    if path and not os.path.supports_unicode_filenames:
        path = path.encode(FSCODING, "replace").decode(FSCODING)
    return path


def get_temp_file(mode='r', **kwargs):
    """Return tuple (open file object, filename) pointing to a temporary
    file."""
    fd, filename = tempfile.mkstemp(**kwargs)
    return os.fdopen(fd, mode), filename


def is_tty(fp):
    """Check if is a file object pointing to a TTY."""
    return hasattr(fp, "isatty") and fp.isatty()


@lru_cache(128)
def is_readable(filename):
    """Check if file is a regular file and is readable."""
    return os.path.isfile(filename) and os.access(filename, os.R_OK)


def is_accessable_by_others(filename):
    """Check if file is group or world accessible."""
    mode = os.stat(filename)[stat.ST_MODE]
    return mode & (stat.S_IRWXG | stat.S_IRWXO)


def is_writable_by_others(filename):
    """Check if file or directory is world writable."""
    mode = os.stat(filename)[stat.ST_MODE]
    return mode & stat.S_IWOTH
