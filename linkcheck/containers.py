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
Special container classes.
"""


class LFUCache(dict):
    """Limited cache which purges least frequently used items."""

    def __init__(self, size=1000):
        """Initialize internal LFU cache."""
        super().__init__()
        if size < 1:
            raise ValueError("invalid cache size %d" % size)
        self.size = size

    def __setitem__(self, key, val):
        """Store given key/value."""
        if key in self:
            # store value, do not increase number of uses
            super().__getitem__(key)[1] = val
        else:
            super().__setitem__(key, [0, val])
            # check for size limit
            if len(self) > self.size:
                self.shrink()

    def shrink(self):
        """Shrink ca. 5% of entries."""
        trim = int(0.05 * len(self))
        if trim:
            items = super().items()
            # sorting function for items
            def keyfunc(x): return x[1][0]
            values = sorted(items, key=keyfunc)
            for item in values[0:trim]:
                del self[item[0]]

    def __getitem__(self, key):
        """Update key usage and return value."""
        entry = super().__getitem__(key)
        entry[0] += 1
        return entry[1]

    def uses(self, key):
        """Get number of uses for given key (without increasing the number of
        uses)"""
        return super().__getitem__(key)[0]

    def get(self, key, def_val=None):
        """Update key usage if found and return value, else return default."""
        if key in self:
            return self[key]
        return def_val

    def setdefault(self, key, def_val=None):
        """Update key usage if found and return value, else set and return
        default."""
        if key in self:
            return self[key]
        self[key] = def_val
        return def_val

    def items(self):
        """Return list of items, not updating usage count."""
        return [(key, value[1]) for key, value in super().items()]

    def iteritems(self):
        """Return iterator of items, not updating usage count."""
        for key, value in super().items():
            yield (key, value[1])

    def values(self):
        """Return list of values, not updating usage count."""
        return [value[1] for value in super().values()]

    def itervalues(self):
        """Return iterator of values, not updating usage count."""
        for value in super().values():
            yield value[1]

    def popitem(self):
        """Remove and return an item."""
        key, value = super().popitem()
        return (key, value[1])

    def pop(self):
        """Remove and return a value."""
        value = super().pop()
        return value[1]
