# Copyright (C) 2010-2014 Bastian Kleineidam
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
"""Parser for Firefox bookmark file."""

import re

try:
    import sqlite3

    has_sqlite = True
except ImportError:
    has_sqlite = False


extension = re.compile(r'/places.sqlite$', re.IGNORECASE)


def parse_bookmark_file(filename):
    """Return iterator for bookmarks of the form (url, name).
    Bookmarks are not sorted.
    Returns None if sqlite3 module is not installed.
    """
    if not has_sqlite:
        return
    conn = sqlite3.connect(filename, timeout=0.5)
    try:
        c = conn.cursor()
        try:
            sql = """SELECT mp.url, mb.title
            FROM moz_places mp, moz_bookmarks mb
            WHERE mp.hidden=0 AND mp.url NOT LIKE 'place:%' AND
            mp.id=mb.fk"""
            c.execute(sql)
            for url, name in c:
                if not name:
                    name = url
                yield (url, name)
        finally:
            c.close()
    finally:
        conn.close()
