import heapq
from typing import ItemsView, Iterable, Tuple

from data import types
from data.graph import bloom_node


class _Cursor(object):
  __slots__ = ('node', '_path')

  def __init__(self, node: bloom_node.BloomNode, path: types.Path) -> None:
    self.node = node
    self._path = path

  def children(self) -> ItemsView['_Cursor', bloom_node.BloomNode]:
    for edge, child in self.node.items():
      yield _alloc(child, (edge, self._path)), child

  def __str__(self) -> str:
    acc = []
    cursor = self._path
    while cursor:
      c, cursor = cursor
      acc.append(c)
    return ''.join(acc[::-1])

  def __repr__(self) -> str:
    return "_Cursor(..., '%s')" % str(self)

def _alloc(node: bloom_node.BloomNode, path: types.Path) -> _Cursor:
  return _Cursor(node, path)


def _free(cursor: _Cursor) -> None:
  del cursor  # Unused argument. Does not actually "free" anything.
  pass


def walk(root: bloom_node.BloomNode) -> Iterable[types.WeightedWord]:
  fringe, pool, free_positions = [], [], []
  def push(cost: float, cursor: _Cursor) -> None:
    if free_positions:
      idx = free_positions.pop()
      pool[idx] = cursor
    else:
      idx = len(pool)
      pool.append(cursor)
    heapq.heappush(fringe, (-cost, idx))
  def pop() -> Tuple[float, _Cursor]:
    weight, idx = heapq.heappop(fringe)
    cursor = pool[idx]
    pool[idx] = None
    free_positions.append(idx)
    return -weight, cursor

  push(float('inf'), _alloc(root, None))
  solutions = []
  while len(fringe):
    weight, cursor = pop()
    while solutions and -solutions[0][0] > weight:
      solution_weight, solution_word = heapq.heappop(solutions)
      yield solution_word, -solution_weight
    for child_cursor, child_node in cursor.children():
      if child_node.match_weight:
        heapq.heappush(solutions, (-child_node.match_weight, str(child_cursor)))
      if child_node:
        push(child_node.max_weight, child_cursor)
    _free(cursor)
  while solutions:
    solution_weight, solution_word = heapq.heappop(solutions)
    yield solution_word, -solution_weight
  if len(pool) > 1000:
    print('WARNING')
    print('Max fringe size was: %s' % len(pool))
