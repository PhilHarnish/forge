import heapq
from typing import Generator, Tuple

from data import types
from data.seek import base_seek, seek_cursor


class Walker(object):
  def __init__(self, seek_root: base_seek.BaseSeek):
    self._seek_root = seek_root

  def __iter__(self) -> Generator[types.WeightedWord, None, None]:
    fringe, pool, free_positions = [], [], []
    def push(cost: float, cursor: seek_cursor.SeekCursor) -> None:
      if free_positions:
        idx = free_positions.pop()
        pool[idx] = cursor
      else:
        idx = len(pool)
        pool.append(cursor)
      heapq.heappush(fringe, (-cost, idx))
    def pop() -> Tuple[float, seek_cursor.SeekCursor]:
      weight, idx = heapq.heappop(fringe)
      cursor = pool[idx]
      pool[idx] = None
      free_positions.append(idx)
      return -weight, cursor
    root = self._seek_root.start()
    max_weight = root.magnitude()

    push(float('inf'), root)
    solutions = []
    while len(fringe):
      weight, cursor = pop()
      for c in cursor.children():
        child = cursor.seek(c)
        match = child.match()
        if match:
          heapq.heappush(solutions, (-match[1], match[0]))
        if child.has_children():
          push(child.magnitude(), child)
      while solutions and -solutions[0][0] > weight:
        solution_weight, solution_word = heapq.heappop(solutions)
        yield solution_word, -solution_weight
    while solutions:
      solution_weight, solution_word = heapq.heappop(solutions)
      yield solution_word, -solution_weight
    if len(pool) > 1000:
      print('WARNING')
      print('Max fringe size was: %s' % len(pool))
