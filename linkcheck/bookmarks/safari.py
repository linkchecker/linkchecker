# Copyright (C) 2011-2014 Bastian Kleineidam
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

import plistlib


def parse_bookmark_data(data):
    """Return iterator for bookmarks of the form (url, name).
    Bookmarks are not sorted.
    """
    return parse_plist(get_plist_data_from_string(data))


def get_plist_data_from_string(data):
    """Parse plist data for a string."""
    try:
        return plistlib.loads(data)
    except Exception:
        # not parseable (eg. not well-formed)
        return {}


# some key strings
KEY_URLSTRING = 'URLString'
KEY_URIDICTIONARY = 'URIDictionary'
KEY_CHILDREN = 'Children'
KEY_WEBBOOKMARKTYPE = 'WebBookmarkType'


def parse_plist(entry):
    """Parse a XML dictionary entry."""
    if is_leaf(entry):
        url = entry[KEY_URLSTRING]
        title = entry[KEY_URIDICTIONARY].get('title', url)
        yield (url, title)
    elif has_children(entry):
        for child in entry[KEY_CHILDREN]:
            yield from parse_plist(child)


def is_leaf(entry):
    """Return true if plist entry is an URL entry."""
    return entry.get(KEY_WEBBOOKMARKTYPE) == 'WebBookmarkTypeLeaf'


def has_children(entry):
    """Return true if plist entry has children."""
    return entry.get(KEY_WEBBOOKMARKTYPE) == 'WebBookmarkTypeList'
