# Group6 - lab 1 - variant 6

## Project structure

- `foo.py` -- implementation of `BinaryTreeDict`: a mutable dictionary
  backed by an unbalanced binary search tree.
- `foo_test.py` -- unit tests and property-based tests (Hypothesis).

## Features

API:

- `set(key, value)` / `add(key, value)` -- insert or overwrite an entry
- `get(key, default=None)` -- look up a value
- `remove(key)` -- delete an entry (no-op if absent)
- `member(key)` -- membership test
- `size()` -- number of entries
- `from_list([(k, v), ...])` -- bulk load
- `to_list()` -- export as sorted list of `(key, value)` pairs
- `filter(pred)` -- keep entries where `pred(key, value)` is True
- `map(func)` -- apply `func` to every value in-place
- `reduce(func, initial)` -- left-fold over `(key, value)` pairs
- `__iter__` / `__next__` -- iterate over keys in ascending order
- `empty()` -- monoid identity (static method)
- `concat(other)` -- monoid binary operation (merge, other wins on conflict)

PBT tests:

- `test_pbt_from_list_roundtrip`
- `test_pbt_size_equals_unique_keys`
- `test_pbt_member_after_set`
- `test_pbt_remove_then_not_member`
- `test_pbt_monoid_right_identity`
- `test_pbt_monoid_left_identity`
- `test_pbt_monoid_associativity`
- `test_pbt_iter_yields_all_keys`
- `test_pbt_map_identity`
- `test_pbt_filter_all_satisfy_predicate`

## Contribution

- Sida JIA 

## Changelog

- 26.04.2025 - 1
  - Add unit tests and PBT tests.
- 26.04.2025 - 0
  - Initial implementation: BinaryTreeDict with full API.

## Design notes

- **Heterogeneous key ordering**: Python 3 cannot compare `None`, `int`,
  and `str` directly. A `_type_rank()` function assigns each type a numeric
  rank (`None=0, bool=1, int=2, float=3, str=4, other=5`), so any two keys
  can be ordered stably without raising `TypeError`.
- **None as key/value**: Both are fully supported. `None` keys sort before
  all other types. `None` values are stored normally; `get()` returning
  `None` is disambiguated by `member()`.
- **Duplicate key semantics**: Following standard dict convention, a second
  `set()` call for an existing key updates the value in-place; size does not
  grow.
- **Deletion**: Uses the classical BST in-order successor strategy for nodes
  with two children.
- **Monoid concat**: When both dictionaries share a key, the value from
  `other` wins. This choice is consistent and makes `concat` associative
  (later writes always dominate).
- **Limitations**: The BST is not self-balancing. In the worst case (sorted
  insertion order) tree height degrades to O(n), making operations O(n)
  instead of O(log n). An AVL or Red-Black tree would address this, but is
  outside the scope of Lab 1.
