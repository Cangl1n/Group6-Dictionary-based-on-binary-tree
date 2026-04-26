import unittest
from hypothesis import given, settings
from hypothesis import strategies as st

from foo import BinaryTreeDict



# Helpers


def make(*pairs) -> BinaryTreeDict:
    d = BinaryTreeDict()
    for k, v in pairs:
        d.set(k, v)
    return d


# size()


class TestSize(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(BinaryTreeDict().size(), 0)

    def test_single(self):
        self.assertEqual(make(("a", 1)).size(), 1)

    def test_multiple(self):
        self.assertEqual(make(("a", 1), ("b", 2), ("c", 3)).size(), 3)

    def test_duplicate_keys_do_not_grow_size(self):
        d = BinaryTreeDict()
        d.set("x", 1)
        d.set("x", 2)
        self.assertEqual(d.size(), 1)



# set() / get() / add()


class TestSetGet(unittest.TestCase):

    def test_set_and_get_basic(self):
        d = BinaryTreeDict()
        d.set("name", "Alice")
        self.assertEqual(d.get("name"), "Alice")

    def test_overwrite_updates_value(self):
        d = BinaryTreeDict()
        d.set("k", 1)
        d.set("k", 99)
        self.assertEqual(d.get("k"), 99)
        self.assertEqual(d.size(), 1)

    def test_get_missing_returns_none(self):
        self.assertIsNone(BinaryTreeDict().get("no-key"))

    def test_get_missing_returns_custom_default(self):
        self.assertEqual(BinaryTreeDict().get("no-key", 42), 42)

    def test_none_key(self):
        d = BinaryTreeDict()
        d.set(None, "null-value")
        self.assertTrue(d.member(None))
        self.assertEqual(d.get(None), "null-value")

    def test_none_value(self):
        d = BinaryTreeDict()
        d.set("key", None)
        self.assertTrue(d.member("key"))
        self.assertIsNone(d.get("key"))

    def test_none_key_and_none_value(self):
        d = BinaryTreeDict()
        d.set(None, None)
        self.assertTrue(d.member(None))
        self.assertIsNone(d.get(None))

    def test_add_is_alias_for_set(self):
        d = BinaryTreeDict()
        d.add("x", 10)
        self.assertEqual(d.get("x"), 10)

    def test_heterogeneous_keys(self):
        d = BinaryTreeDict()
        d.set(None, "none-val")
        d.set(1, "int-val")
        d.set("s", "str-val")
        self.assertEqual(d.get(None), "none-val")
        self.assertEqual(d.get(1), "int-val")
        self.assertEqual(d.get("s"), "str-val")
        self.assertEqual(d.size(), 3)



# remove()

class TestRemove(unittest.TestCase):

    def test_remove_existing(self):
        d = make(("a", 1), ("b", 2))
        d.remove("a")
        self.assertFalse(d.member("a"))
        self.assertTrue(d.member("b"))

    def test_remove_nonexistent_is_noop(self):
        d = make(("a", 1))
        d.remove("zzz")          # must not raise
        self.assertEqual(d.size(), 1)

    def test_remove_none_key(self):
        d = make((None, "x"), ("a", 1))
        d.remove(None)
        self.assertFalse(d.member(None))
        self.assertTrue(d.member("a"))

    def test_remove_all(self):
        d = make(("a", 1), ("b", 2))
        d.remove("a")
        d.remove("b")
        self.assertEqual(d.size(), 0)

    def test_remove_root(self):
        d = make((10, "ten"))
        d.remove(10)
        self.assertEqual(d.size(), 0)
        self.assertFalse(d.member(10))

    def test_remove_node_with_two_children(self):
        d = make((5, "five"), (3, "three"), (7, "seven"))
        d.remove(5)
        self.assertFalse(d.member(5))
        self.assertTrue(d.member(3))
        self.assertTrue(d.member(7))
        self.assertEqual(d.size(), 2)



# member()


class TestMember(unittest.TestCase):

    def test_not_member_empty(self):
        self.assertFalse(BinaryTreeDict().member("k"))

    def test_member_found(self):
        self.assertTrue(make(("x", 1)).member("x"))

    def test_member_none_key(self):
        d = make((None, "v"))
        self.assertTrue(d.member(None))
        self.assertFalse(d.member("other"))

    def test_not_member_after_remove(self):
        d = make(("a", 1))
        d.remove("a")
        self.assertFalse(d.member("a"))



# from_list() / to_list()


class TestConversion(unittest.TestCase):

    def test_from_list_empty(self):
        d = BinaryTreeDict()
        d.from_list([])
        self.assertEqual(d.size(), 0)
        self.assertEqual(d.to_list(), [])

    def test_round_trip(self):
        pairs = [("a", 1), ("b", 2), ("c", 3)]
        d = BinaryTreeDict()
        d.from_list(pairs)
        self.assertEqual(set(d.to_list()), set(pairs))

    def test_from_list_duplicate_last_wins(self):
        d = BinaryTreeDict()
        d.from_list([("k", 1), ("k", 99)])
        self.assertEqual(d.get("k"), 99)
        self.assertEqual(d.size(), 1)

    def test_to_list_inorder_for_ints(self):
        d = BinaryTreeDict()
        d.from_list([(3, "c"), (1, "a"), (2, "b")])
        keys = [k for k, _ in d.to_list()]
        self.assertEqual(keys, sorted(keys))

    def test_none_key_in_list(self):
        d = BinaryTreeDict()
        d.from_list([(None, "n"), (1, "i")])
        self.assertEqual(d.get(None), "n")
        self.assertEqual(d.get(1), "i")



# filter()


class TestFilter(unittest.TestCase):

    def test_filter_by_value(self):
        d = make((1, 10), (2, 20), (3, 30))
        d.filter(lambda k, v: v > 15)
        self.assertFalse(d.member(1))
        self.assertTrue(d.member(2))
        self.assertTrue(d.member(3))

    def test_filter_by_key(self):
        d = make(("a", 1), ("b", 2), ("c", 3))
        d.filter(lambda k, v: k != "b")
        self.assertFalse(d.member("b"))
        self.assertTrue(d.member("a"))
        self.assertTrue(d.member("c"))

    def test_filter_removes_none_key(self):
        d = make((None, "n"), (1, "i"))
        d.filter(lambda k, v: k is not None)
        self.assertFalse(d.member(None))
        self.assertTrue(d.member(1))

    def test_filter_all_removed(self):
        d = make(("a", 1), ("b", 2))
        d.filter(lambda k, v: False)
        self.assertEqual(d.size(), 0)



# map()

class TestMap(unittest.TestCase):

    def test_map_values(self):
        d = make(("a", 1), ("b", 2))
        d.map(lambda v: v * 10)
        self.assertEqual(d.get("a"), 10)
        self.assertEqual(d.get("b"), 20)

    def test_map_empty_no_error(self):
        BinaryTreeDict().map(str)

    def test_map_none_value(self):
        d = make(("k", None))
        d.map(lambda v: "was-none" if v is None else v)
        self.assertEqual(d.get("k"), "was-none")



# reduce()


class TestReduce(unittest.TestCase):

    def test_reduce_empty(self):
        self.assertEqual(BinaryTreeDict().reduce(lambda a, kv: a + kv[1], 0), 0)

    def test_reduce_sum_values(self):
        d = make(("a", 1), ("b", 2), ("c", 3))
        self.assertEqual(d.reduce(lambda a, kv: a + kv[1], 0), 6)

    def test_reduce_collect_keys(self):
        d = make(("x", 10), ("y", 20))
        keys = d.reduce(lambda a, kv: a + [kv[0]], [])
        self.assertEqual(set(keys), {"x", "y"})

    def test_reduce_count_entries(self):
        d = BinaryTreeDict()
        d.from_list([("a", 1), ("b", 2), ("c", 3)])
        count = d.reduce(lambda a, _: a + 1, 0)
        self.assertEqual(count, d.size())



# Iterator


class TestIterator(unittest.TestCase):

    def test_iter_empty(self):
        self.assertEqual(list(BinaryTreeDict()), [])

    def test_iter_yields_all_keys(self):
        d = make(("a", 1), ("b", 2), ("c", 3))
        self.assertEqual(set(d), {"a", "b", "c"})

    def test_iter_sorted_ints(self):
        d = make((3, "c"), (1, "a"), (2, "b"))
        self.assertEqual(list(d), [1, 2, 3])

    def test_iter_includes_none_key(self):
        d = make((None, "n"), (1, "i"))
        self.assertIn(None, list(d))
        self.assertIn(1, list(d))

    def test_stopiteration_on_empty(self):
        it = iter(BinaryTreeDict())
        with self.assertRaises(StopIteration):
            next(it)



# Monoid


class TestMonoid(unittest.TestCase):

    def test_empty_has_zero_size(self):
        self.assertEqual(BinaryTreeDict.empty().size(), 0)

    def test_concat_disjoint(self):
        d1 = make(("a", 1))
        d1.concat(make(("b", 2)))
        self.assertEqual(d1.size(), 2)

    def test_concat_right_identity(self):
        d = make(("a", 1), ("b", 2))
        before = d.to_list()
        d.concat(BinaryTreeDict.empty())
        self.assertEqual(d.to_list(), before)

    def test_concat_left_identity(self):
        e = BinaryTreeDict.empty()
        other = make(("a", 1))
        e.concat(other)
        self.assertTrue(e.member("a"))

    def test_concat_overlap_other_wins(self):
        d1 = make(("k", "original"))
        d1.concat(make(("k", "override")))
        self.assertEqual(d1.get("k"), "override")

    def test_concat_with_none_key(self):
        d1 = make((None, "a"))
        d1.concat(make((1, "b")))
        self.assertTrue(d1.member(None))
        self.assertTrue(d1.member(1))



# Property-Based Tests (Hypothesis)


_keys = st.one_of(st.none(), st.integers(), st.text(max_size=5))
_values = st.one_of(st.none(), st.integers(), st.text(max_size=5))
_pairs = st.lists(st.tuples(_keys, _values), max_size=20)


class TestPBT(unittest.TestCase):

    @given(_pairs)
    def test_pbt_from_list_roundtrip(self, pairs):
        """All entries inserted via from_list() must be retrievable."""
        d = BinaryTreeDict()
        d.from_list(pairs)
        result = dict(d.to_list())
        expected = {}
        for k, v in pairs:
            expected[k] = v
        self.assertEqual(result, expected)

    @given(_pairs)
    def test_pbt_size_equals_unique_keys(self, pairs):
        d = BinaryTreeDict()
        d.from_list(pairs)
        self.assertEqual(d.size(), len({k for k, _ in pairs}))

    @given(_pairs)
    def test_pbt_member_after_set(self, pairs):
        d = BinaryTreeDict()
        for k, v in pairs:
            d.set(k, v)
        for k, _ in pairs:
            self.assertTrue(d.member(k))

    @given(_pairs)
    def test_pbt_remove_then_not_member(self, pairs):
        if not pairs:
            return
        d = BinaryTreeDict()
        d.from_list(pairs)
        key = pairs[0][0]
        d.remove(key)
        self.assertFalse(d.member(key))

    @given(_pairs)
    def test_pbt_monoid_right_identity(self, pairs):
        d = BinaryTreeDict()
        d.from_list(pairs)
        before = dict(d.to_list())
        d.concat(BinaryTreeDict.empty())
        self.assertEqual(dict(d.to_list()), before)

    @given(_pairs)
    def test_pbt_monoid_left_identity(self, pairs):
        d = BinaryTreeDict()
        d.from_list(pairs)
        expected = dict(d.to_list())
        e = BinaryTreeDict.empty()
        e.concat(d)
        self.assertEqual(dict(e.to_list()), expected)

    @given(_pairs, _pairs, _pairs)
    @settings(max_examples=50)
    def test_pbt_monoid_associativity(self, pa, pb, pc):
        """(a⊕b)⊕c == a⊕(b⊕c)"""
        def build(pairs):
            d = BinaryTreeDict()
            d.from_list(pairs)
            return d

        left = build(pa)
        left.concat(build(pb))
        left.concat(build(pc))

        bc = build(pb)
        bc.concat(build(pc))
        right = build(pa)
        right.concat(bc)

        self.assertEqual(dict(left.to_list()), dict(right.to_list()))

    @given(_pairs)
    def test_pbt_iter_yields_all_keys(self, pairs):
        d = BinaryTreeDict()
        d.from_list(pairs)
        self.assertEqual(set(d), {k for k, _ in pairs})

    @given(_pairs)
    def test_pbt_map_identity(self, pairs):
        d = BinaryTreeDict()
        d.from_list(pairs)
        before = dict(d.to_list())
        d.map(lambda v: v)
        self.assertEqual(dict(d.to_list()), before)

    @given(_pairs)
    def test_pbt_filter_all_satisfy_predicate(self, pairs):
        d = BinaryTreeDict()
        d.from_list(pairs)
        pred = lambda k, v: v is not None
        d.filter(pred)
        for k, v in d.to_list():
            self.assertTrue(pred(k, v))


if __name__ == "__main__":
    unittest.main()
