import heapq


class MaxHeap(object):
  def __init__(self):
    self._heap = []
    self._pool = []
    self._free_positions = []

  def __len__(self):
    return len(self._heap)

  def push(self, cost, o):
    if self._free_positions:
      idx = self._free_positions.pop()
      self._pool[idx] = o
    else:
      idx = len(self._pool)
      self._pool.append(o)
    heapq.heappush(self._heap, (-cost, idx))

  def best_weight(self):
    return -self._heap[0][0]

  def pop(self):
    _, idx = heapq.heappop(self._heap)
    result = self._pool[idx]
    self._pool[idx] = None
    self._free_positions.append(idx)
    return result
