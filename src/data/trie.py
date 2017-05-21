import heapq


class Trie(object):
  def __init__(self, data):
    self._smallest = float('inf')
    # Trie's index (highest value characters first).
    self._index = []
    self._len = 0
    for key, value in data:
      self[key] = value

  def __contains__(self, key):
    result = self._find_prefix(key)
    return result is not None and result[2] > 0

  def __len__(self):
    return self._len

  def __setitem__(self, key, value, *args, **kwargs):
    if value > self._smallest:
      raise AssertionError('Items must be added to trie in descending order.')
    else:
      self._smallest = value
    self._add_to_index(key, value)

  def __getitem__(self, key):
    result = self._find_prefix(key)
    if result is None or result[2] == 0:
      raise KeyError('%s not in Trie' % key)
    return result[2]

  def has_keys_with_prefix(self, prefix):
    return self._find_prefix(prefix) is not None

  def _find_prefix(self, prefix):
    l = len(prefix)
    pos = 0
    cursor = self._index
    searching = True
    result = cursor
    while searching and pos < l:
      searching = False
      target = prefix[pos]
      for row in cursor:
        if len(row) == 3:
          dst_c, _, _ = row
          children = None
        else:
          dst_c, _, _, *children = row
        if dst_c == target:
          result = row
          pos += 1
          if children:
            searching = True
            cursor = children
          break
    if pos == l:
      return result
    return None

  def walk(self, seek_sets):
    """Returns solutions matching `seek_sets`, ordered from high to low."""
    # TODO: Inline per findings from commit 47a736f.
    fringe = _MaxHeap()
    solutions = _MaxHeap()
    acc = []
    fringe.push(float('inf'), (acc, self._index))
    stop_seek_pos = len(seek_sets) - 1
    while len(fringe):
      fringe_score = fringe.best_weight()  # Already normalized.
      acc, children = fringe.pop()
      pos = len(acc)
      seeking = seek_sets[pos]
      for row in children:
        if len(row) == 3:
          c, magnitude, match_weight = row
          next_children = None
        else:
          c, magnitude, match_weight, *next_children = row
        if c not in seeking:
          continue
        acc.append(c)
        if match_weight:
          solutions.push(match_weight, ''.join(acc))
        if next_children and pos < stop_seek_pos:
          fringe.push(magnitude, (acc[:], next_children))
        acc.pop()
      while len(solutions) and solutions.best_weight() >= fringe_score:
        solution_weight = solutions.best_weight()
        yield solutions.pop(), solution_weight
    while len(solutions):
      solution_weight = solutions.best_weight()
      yield solutions.pop(), solution_weight

      # print('Max fringe size was: %s' % len(fringe._pool))
      # print('Max solution buffer size was: %s' % len(solutions._pool))

  def _add_to_index(self, word, weight):
    # TODO: This takes ~5 seconds to initialize with massive data.
    l = len(word)
    cursor = self._index
    pos = 0
    searching = True
    add_to_cursor = cursor
    while searching and pos < l:
      searching = False
      target = word[pos]
      for row in cursor:
        if len(row) == 3:
          dst_c, _, match_weight = row
          children = None
        else:
          dst_c, _, match_weight, *children = row
        if dst_c == target:
          pos += 1
          if pos == l:
            if match_weight:
              # Duplicate addition.
              raise KeyError('%s already added' % word)
            # Exhausted input; this spells something now.
            row[2] = weight
            self._len += 1
            return
          elif children:
            # More children to consider.
            searching = True
            cursor = children
          # Update location to add word to.
          add_to_cursor = row
          break
    end = len(word) - 1
    for i in range(pos, len(word)):
      if i == end:
        add_to_cursor.append([word[i], weight, weight])
      else:
        new_cursor = [word[i], weight, 0]
        add_to_cursor.append(new_cursor)
        add_to_cursor = new_cursor
    self._len += 1


class _MaxHeap(object):
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

  def get_min(self):
    _, min_idx = self._heap[0]
    return self._pool[min_idx]

  def best_weight(self):
    return -self._heap[0][0]

  def pop(self):
    _, idx = heapq.heappop(self._heap)
    result = self._pool[idx]
    self._pool[idx] = None
    self._free_positions.append(idx)
    return result

  def replace_min(self, cost, o):
    _, min_idx = self._heap[0]  # Peek at min for idx.
    self._pool[min_idx] = o  # Reuse that idx.
    heapq.heapreplace(self._heap, (-cost, min_idx))
