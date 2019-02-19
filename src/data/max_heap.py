import heapq
from typing import Generic, Iterable, Tuple, TypeVar

T = TypeVar('T')


class MaxHeap(Generic[T]):
  def __init__(self) -> None:
    self._heap = []
    self._pool = []
    self._free_positions = []

  def __len__(self) -> int:
    return len(self._heap)

  def push(self, cost: float, o: T) -> None:
    if self._free_positions:
      idx = self._free_positions.pop()
      self._pool[idx] = o
    else:
      idx = len(self._pool)
      self._pool.append(o)
    heapq.heappush(self._heap, (-cost, idx))

  def best_weight(self) -> float:
    return -self._heap[0][0]

  def pop(self) -> T:
    return self.pop_with_weight()[0]

  def pop_with_weight(self) -> Tuple[T, float]:
    weight, idx = heapq.heappop(self._heap)
    result = self._pool[idx]
    self._pool[idx] = None
    self._free_positions.append(idx)
    return result, -weight

  def pop_with_weight_until(
      self, threshold: float) -> Iterable[Tuple[T, float]]:
    while self._heap and self.best_weight() >= threshold:
      yield self.pop_with_weight()
