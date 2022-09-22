"""
Test the anchor.py cache
"""
import unittest

from linkcheck.cache import anchor


class AnchorCacheTest(unittest.TestCase):
    """ Various test cases """

    def setUp(self):
        self.default_key = 'some_key'
        self.default_type = 'some_type'
        self.default_value = 'some_value'

    def test_none_handling(self):
        cache = anchor.AnchorCache(100)  # far more than we need

        assert cache.get(self.default_key, self.default_type) is None, \
            "We can get from an unused cache without a crash"
        assert cache.get(None, None) is None, \
            "We can safely pass None to both arguments"
        assert cache.get(self.default_key, None) is None, \
            "We can safely pass None as the type argument"

    def test_regular_cache(self):
        cache = anchor.AnchorCache(100)  # far more than we need

        cache.put(self.default_key, self.default_type, self.default_value)
        assert cache.get(self.default_key, self.default_type) is self.default_value, \
            "The cache will store and return our items"

        new_value = 'some_new_value'
        cache.put(self.default_key, self.default_type, new_value)
        assert cache.get(self.default_key, self.default_type) is new_value, \
            "We can overwrite cache values"

        new_type = 'some_new_type'
        cache.put(self.default_key, new_type, self.default_value)
        assert cache.get(self.default_key, new_type) is self.default_value, \
            "We can store new types for the same key"
        assert cache.get(self.default_key, self.default_type) is new_value, \
            "...without altering the values of other types on that key"

        new_key = 'some_new_key'
        cache.put(new_key, self.default_type, self.default_value)
        assert cache.get(new_key, self.default_type) is self.default_value, \
            "We can add and retrieve a second item"
        assert cache.get(self.default_key, new_type) is self.default_value, \
            "...without altering existing items"
        assert cache.get(self.default_key, self.default_type) is new_value, \
            "...regardless of type"

    def test_zero_cache(self):
        cache = anchor.AnchorCache(0)

        cache.put(self.default_key, self.default_type, self.default_value)
        assert cache.get(self.default_key, self.default_type) is None, \
            "A cache with a limit of 0 stores nothing"

    def test_one_cache(self):
        cache = anchor.AnchorCache(1)

        cache.put(self.default_key, self.default_type, self.default_value)
        assert cache.get(self.default_key, self.default_type) is self.default_value, \
            "A 1 cache will store and return one item"

        new_type = 'some_new_type'
        cache.put(self.default_key, new_type, self.default_value)
        assert cache.get(self.default_key, new_type) is self.default_value, \
            "A new type on the same key is fine, in a 1 cache"
        assert cache.get(self.default_key, self.default_type) is self.default_value, \
            "...and the original type is preserved, in a 1 cache"

        new_key = 'some_new_key'
        new_value = 'new_value_just_to_be_sure'
        cache.put(new_key, self.default_type, new_value)
        assert cache.get(new_key, self.default_type) is new_value, \
            "We can store and retrieve a second item in a 1 cache"
        assert cache.get(self.default_key, self.default_type) is None, \
            "...but it deletes the first item"

        another_new_key = 'another_new_key'
        cache.put(another_new_key, self.default_type, self.default_value)
        assert cache.get(another_new_key, self.default_type) is self.default_value, \
            "We can store and retrieve a third item in a 1 cache"
        assert cache.get(new_key, self.default_type) is None, \
            "...but it deletes the second item"

    def test_N_cache(self):
        cache = anchor.AnchorCache(5)  # enough to be sure we aren't just getting lucky

        def key(i):
            return f"key {i}"

        new_type = 'new_type'
        another_new_type = 'another_new_type'
        new_value = 'new_value'

        for i in range(1, 11):  # i.e. 1 to 10
            cache.put(key(i), self.default_type, self.default_value)
            cache.put(key(i), new_type, self.default_value)
            cache.put(key(i), another_new_type, new_value)

        for i in range(1, 6):
            assert cache.get(key(i), self.default_type) is None, \
                f"Item {i} was pushed out"
            assert cache.get(key(i), new_type) is None, \
                f"Item {i} was pushed out, no matter what type we ask for"

        for i in range(6, 11):
            assert cache.get(key(i), self.default_type) == self.default_value, \
                f"Item {i} is still there"
            assert cache.get(key(i), new_type) == self.default_value, \
                f"Item {i} is still there, with the new type"
            assert cache.get(key(i), another_new_type) == new_value, \
                f"Item {i} is still there, with another new type"

    def test_N_cache_mixed(self):
        cache = anchor.AnchorCache(3)

        def key(i):
            return f"key {i}"

        for i in range(1, 4):  # i.e. 1 to 3
            cache.put(key(i), self.default_type, self.default_value)

        assert cache.get(key(1), self.default_type) is self.default_value, \
            "Item 1 is still there"

        # now add a new type to #1, so it is modified most-recently
        new_type = 'new_type'
        cache.put(key(1), new_type, self.default_value)

        for i in range(1, 4):
            assert cache.get(key(i), self.default_type) is self.default_value, \
                f"Item {i} is still there"

        cache.put(key(4), self.default_type, self.default_value)
        assert cache.get(key(1), self.default_type) is None, \
            "Item 1 was pushed out, even though it was most-recently modified"
