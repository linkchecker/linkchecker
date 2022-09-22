"""
Multi-data-type cache for AnchorCheck optimization.
This helps save time redoing work for the same URL where the only difference
is the anchor. It's only a partial fix for the problem, though; we still make
multiple connections to the same server for the same url. A "real" fix would
require a deeper design change to the whole linkcheck algorithm.
"""
from ..decorators import synchronized
from ..lock import get_lock

cache_lock = get_lock("anchor_cache_lock")


class AnchorCache:
    """
    Thread-safe cache of multiple data types, all based on the URL with the
    anchor stripped.
    The cache is limited in size since we'd rather recheck the same URL
    multiple times instead of running out of memory.
    format: {url w/o anchor -> { <type>: <object>, <other type>: <other object>, ... } }
    """

    def __init__(self, anchor_cache_size):
        """Initialize anchor cache."""
        self.cache = {}
        self.cache_order = []
        self.cache_delete_index = 0
        self.max_size = anchor_cache_size

    @synchronized(cache_lock)
    def get(self, cache_key, cache_type):
        """Return cached data or None if not found."""
        if cache_key is not None:
            record = self.cache.get(cache_key)
            if record is not None:
                return record.get(cache_type)
        return None

    @synchronized(cache_lock)
    def put(self, cache_key, cache_type, cache_object):
        """
        Add object to cache with given key, categorized appropriately.
        Delete old cache objects if the cache is full.
        """
        if cache_key is not None:
            record = self.cache.get(cache_key)
            if record is None:
                record = {}
                self.cache_order.append(cache_key)
            record[cache_type] = cache_object
            self.cache[cache_key] = record

        if len(self.cache) > self.max_size:
            del self.cache[self.cache_order[self.cache_delete_index]]
            self.cache_delete_index += 1
