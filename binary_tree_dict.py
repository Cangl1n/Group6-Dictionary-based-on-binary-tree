"""
Lab 1 - Variant (6): Mutable Dictionary based on Binary Search Tree
"""

from __future__ import annotations
from typing import Any, Callable, Iterator, List, Optional, Tuple


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
        return a < b  # type: ignore[operator]
    except TypeError:
        return repr(a) < repr(b)


def _key_eq(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a == b


class _Node:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key: Any, value: Any) -> None:
        self.key: Any = key
        self.value: Any = value
        self.left: Optional[_Node] = None
        self.right: Optional[_Node] = None


class BinaryTreeDict:
    """Mutable dictionary backed by an unbalanced binary search tree."""

    def __init__(self) -> None:
        self._root: Optional[_Node] = None

    def add(self, key: Any, value: Any) -> None:
        """Add or update an entry. Alias for set()."""
        self.set(key, value)

    def set(self, key: Any, value: Any) -> None:
        """Set key to value. Inserts if new; overwrites if key exists."""
        self._root = self._insert(self._root, key, value)

    def _insert(
        self, node: Optional[_Node], key: Any, value: Any
    ) -> _Node:
        if node is None:
            return _Node(key, value)
        if _key_eq(key, node.key):
            node.value = value
        elif _key_lt(key, node.key):
            node.left = self._insert(node.left, key, value)
        else:
            node.right = self._insert(node.right, key, value)
        return node

    def get(self, key: Any, default: Any = None) -> Any:
        """Return value for key, or default if absent."""
        node = self._find(self._root, key)
        return node.value if node is not None else default

    def _find(
        self, node: Optional[_Node], key: Any
    ) -> Optional[_Node]:
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

    def remove(self, key: Any) -> None:
        """Remove key. No-op if key is absent."""
        self._root = self._delete(self._root, key)

    def _delete(
        self, node: Optional[_Node], key: Any
    ) -> Optional[_Node]:
        if node is None:
            return None
        if _key_eq(key, node.key):
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
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

    def to_list(self) -> List[Tuple[Any, Any]]:
        """Return all (key, value) pairs in ascending key order."""
        result: List[Tuple[Any, Any]] = []
        self._inorder(self._root, result)
        return result

    def _inorder(
        self, node: Optional[_Node], result: List[Tuple[Any, Any]]
    ) -> None:
        if node is None:
            return
        self._inorder(node.left, result)
        result.append((node.key, node.value))
        self._inorder(node.right, result)

    def from_list(self, lst: List[Tuple[Any, Any]]) -> None:
        """Load from a list of (key, value) tuples. Later entries win."""
        self._root = None
        for key, value in lst:
            self.set(key, value)

    def filter(
        self, predicate: Callable[[Any, Any], bool]
    ) -> None:
        """Keep only entries where predicate(key, value) is True."""
        keep = [(k, v) for k, v in self.to_list() if predicate(k, v)]
        self._root = None
        for k, v in keep:
            self.set(k, v)

    def map(self, func: Callable[[Any], Any]) -> None:
        """Apply func to every value in-place."""
        self._map_node(self._root, func)

    def _map_node(
        self, node: Optional[_Node], func: Callable[[Any], Any]
    ) -> None:
        if node is None:
            return
        node.value = func(node.value)
        self._map_node(node.left, func)
        self._map_node(node.right, func)

    def reduce(
        self,
        func: Callable[[Any, Tuple[Any, Any]], Any],
        initial: Any,
    ) -> Any:
        """Left-fold over (key, value) pairs in in-order sequence.

        func(accumulator, (key, value)) -> new_accumulator
        """
        state = initial
        for kv in self.to_list():
            state = func(state, kv)
        return state

    def __iter__(self) -> Iterator[Any]:
        self._iter_stack: List[_Node] = []
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

    @staticmethod
    def empty() -> "BinaryTreeDict":
        """Identity element of the monoid."""
        return BinaryTreeDict()

    def concat(self, other: "BinaryTreeDict") -> None:
        """Merge other into self. Keys from other override keys in self.

        Satisfies monoid laws:
          left identity  : empty().concat(d)  == d
          right identity : d.concat(empty())  == d
          associativity  : (a+b)+c            == a+(b+c)
        """
        for k, v in other.to_list():
            self.set(k, v)

    def __str__(self) -> str:
        inner = ", ".join(
            f"{repr(k)}: {repr(v)}" for k, v in self.to_list()
        )
        return "{" + inner + "}"

    def __repr__(self) -> str:
        return f"BinaryTreeDict({str(self)})"

    def __eq__(self, other: object) -> bool:
        """Efficient equality: simultaneous in-order traversal.

        Avoids building two full lists; exits as soon as a difference
        is found, giving O(k) time where k is the position of the
        first differing element.
        """
        if not isinstance(other, BinaryTreeDict):
            return NotImplemented
        left_iter = _InorderIter(self._root)
        right_iter = _InorderIter(other._root)
        while True:
            lv = next(left_iter, None)
            rv = next(right_iter, None)
            if lv is None and rv is None:
                return True
            if lv is None or rv is None:
                return False
            lk, lval = lv
            rk, rval = rv
            if not _key_eq(lk, rk) or lval != rval:
                return False


class _InorderIter:
    """Iterates (key, value) pairs of a BST in ascending key order."""

    def __init__(self, root: Optional[_Node]) -> None:
        self._stack: List[_Node] = []
        self._cur: Optional[_Node] = root

    def __iter__(self) -> "_InorderIter":
        return self

    def __next__(self) -> Optional[Tuple[Any, Any]]:
        while self._cur is not None or self._stack:
            while self._cur is not None:
                self._stack.append(self._cur)
                self._cur = self._cur.left
            self._cur = self._stack.pop()
            pair: Tuple[Any, Any] = (self._cur.key, self._cur.value)
            self._cur = self._cur.right
            return pair
        raise StopIteration
