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

import json


def parse_bookmark_data(data):
    """Parse data string.
    Return iterator for bookmarks of the form (url, name).
    Bookmarks are not sorted.
    """
    yield from parse_bookmark_json(json.loads(data))


def parse_bookmark_json(data):
    """Parse complete JSON data for Chromium Bookmarks."""
    for entry in data["roots"].values():
        yield from parse_bookmark_node(entry)


def parse_bookmark_node(node):
    """Parse one JSON node of Chromium Bookmarks."""
    if node["type"] == "url":
        yield node["url"], node["name"]
    elif node["type"] == "folder":
        for child in node["children"]:
            yield from parse_bookmark_node(child)
