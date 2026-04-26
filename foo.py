"""
Lab 1 — Variant (6): Mutable Dictionary based on Binary Search Tree
====================================================================
A mutable dictionary implemented using an unbalanced BST.

Key design decisions:
- Mixed-type keys (None, int, str, …) are supported via a stable
  ordering function:  None < bool < int < float < str < other.
- Duplicate keys update the value in-place (standard dict semantics).
- All mutating methods operate in-place and return None.
- concat() treats keys from `other` as overriding keys in `self`.
"""

from __future__ import annotations
from typing import Any, Callable, Iterator, Optional



# Ordering helpers for heterogeneous keys


def _type_rank(key: Any) -> int:
    if key is None:
        return 0
    if isinstance(key, bool):
        return 1
    if isinstance(key, int):
        return 2
    if isinstance(key, float):
        return 3
    if isinstance(key, str):
        return 4
    return 5


def _key_lt(a: Any, b: Any) -> bool:
    ra, rb = _type_rank(a), _type_rank(b)
    if ra != rb:
        return ra < rb
    if a is None:
        return False
    try:
        return a < b   # type: ignore[operator]
    except TypeError:
        return repr(a) < repr(b)


def _key_eq(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a == b



# Internal BST node


class _Node:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key: Any, value: Any) -> None:
        self.key = key
        self.value = value
        self.left:  Optional[_Node] = None
        self.right: Optional[_Node] = None



# Public class


class BinaryTreeDict:
    """Mutable dictionary backed by an unbalanced binary search tree."""

    def __init__(self) -> None:
        self._root: Optional[_Node] = None


    #  Insert / update                                                     #


    def add(self, key: Any, value: Any) -> None:
        """Add or update an entry. Alias for set()."""
        self.set(key, value)

    def set(self, key: Any, value: Any) -> None:
        """Set key → value. Inserts if new; overwrites if key exists."""
        self._root = self._insert(self._root, key, value)

    def _insert(self, node: Optional[_Node], key: Any, value: Any) -> _Node:
        if node is None:
            return _Node(key, value)
        if _key_eq(key, node.key):
            node.value = value
        elif _key_lt(key, node.key):
            node.left = self._insert(node.left, key, value)
        else:
            node.right = self._insert(node.right, key, value)
        return node


    #  Lookup                                                              #


    def get(self, key: Any, default: Any = None) -> Any:
        """Return value for key, or default if absent."""
        node = self._find(self._root, key)
        return node.value if node is not None else default

    def _find(self, node: Optional[_Node], key: Any) -> Optional[_Node]:
        if node is None:
            return None
        if _key_eq(key, node.key):
            return node
        if _key_lt(key, node.key):
            return self._find(node.left, key)
        return self._find(node.right, key)

    def member(self, key: Any) -> bool:
        """Return True if key is present."""
        return self._find(self._root, key) is not None

    def size(self) -> int:
        """Return number of key-value pairs."""
        return self._size(self._root)

    def _size(self, node: Optional[_Node]) -> int:
        if node is None:
            return 0
        return 1 + self._size(node.left) + self._size(node.right)


    #  Deletion                                                            #


    def remove(self, key: Any) -> None:
        """Remove key. No-op if key is absent."""
        self._root = self._delete(self._root, key)

    def _delete(self, node: Optional[_Node], key: Any) -> Optional[_Node]:
        if node is None:
            return None
        if _key_eq(key, node.key):
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Two children: replace with in-order successor
            succ = self._min_node(node.right)
            node.key, node.value = succ.key, succ.value
            node.right = self._delete(node.right, succ.key)
        elif _key_lt(key, node.key):
            node.left = self._delete(node.left, key)
        else:
            node.right = self._delete(node.right, key)
        return node

    def _min_node(self, node: _Node) -> _Node:
        cur = node
        while cur.left is not None:
            cur = cur.left
        return cur


    #  Conversion                                                          #


    def to_list(self) -> list:
        """Return all (key, value) pairs in ascending key order."""
        result: list = []
        self._inorder(self._root, result)
        return result

    def _inorder(self, node: Optional[_Node], result: list) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append((node.key, node.value))
        self._inorder(node.right, result)

    def from_list(self, lst: list) -> None:
        """Load from a list of (key, value) tuples. Later entries win."""
        self._root = None
        for key, value in lst:
            self.set(key, value)


    #  Functional operations                                               #


    def filter(self, predicate: Callable[[Any, Any], bool]) -> None:
        """Keep only entries where predicate(key, value) is True."""
        keep = [(k, v) for k, v in self.to_list() if predicate(k, v)]
        self._root = None
        for k, v in keep:
            self.set(k, v)

    def map(self, func: Callable[[Any], Any]) -> None:
        """Apply func to every value in-place."""
        self._map_node(self._root, func)

    def _map_node(self, node: Optional[_Node], func: Callable) -> None:
        if node is None:
            return
        node.value = func(node.value)
        self._map_node(node.left, func)
        self._map_node(node.right, func)

    def reduce(self, func: Callable[[Any, tuple], Any], initial: Any) -> Any:
        """Left-fold over (key, value) pairs in in-order sequence.

        func(accumulator, (key, value)) → new_accumulator
        """
        state = initial
        for kv in self.to_list():
            state = func(state, kv)
        return state


    #  Iterator (yields keys in sorted order)                             #


    def __iter__(self) -> Iterator:
        self._iter_stack: list = []
        self._iter_cur: Optional[_Node] = self._root
        return self

    def __next__(self) -> Any:
        while self._iter_cur is not None or self._iter_stack:
            while self._iter_cur is not None:
                self._iter_stack.append(self._iter_cur)
                self._iter_cur = self._iter_cur.left
            self._iter_cur = self._iter_stack.pop()
            key = self._iter_cur.key
            self._iter_cur = self._iter_cur.right
            return key
        raise StopIteration


    #  Monoid                                                              #


    @staticmethod
    def empty() -> "BinaryTreeDict":
        """Identity element of the monoid."""
        return BinaryTreeDict()

    def concat(self, other: "BinaryTreeDict") -> None:
        """Merge other into self. Keys from other override keys in self.

        Satisfies monoid laws:
          left identity  : empty().concat(d)  ≡ d
          right identity : d.concat(empty())  ≡ d
          associativity  : (a⊕b)⊕c           ≡ a⊕(b⊕c)
        """
        for k, v in other.to_list():
            self.set(k, v)


    #  Display                                                             #


    def __str__(self) -> str:
        inner = ", ".join(f"{repr(k)}: {repr(v)}" for k, v in self.to_list())
        return "{" + inner + "}"

    def __repr__(self) -> str:
        return f"BinaryTreeDict({str(self)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinaryTreeDict):
            return NotImplemented
        return self.to_list() == other.to_list()
