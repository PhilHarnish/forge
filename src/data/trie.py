import heapq

from data.seek_sets import base_seek_set


class Trie(object):
  def __init__(self, data):
    self._smallest = float('inf')
    self._largest = 0
    # Trie's index (highest value characters first).
    self._index = {
      'max_length': 0,
    }
    self._len = 0
    values = []
    for key, value in data:
      if not self._largest:
        self._largest = value
      if value > self._smallest:
        raise AssertionError(
            'Items must be added to trie in descending order.')
      else:
        self._smallest = value
      self._add_to_index(key, value)
      values.append(value)
    num_values = len(values)
    if num_values % 2:
      self._percentile25 = values[num_values // 8 + 1]
    else:
      self._percentile25 = (
        (values[num_values // 8 - 1] + values[num_values // 8]) / 2)

  def __contains__(self, key):
    result = self._find_prefix(key)
    return result is not None and result['match_weight'] > 0

  def __len__(self):
    return self._len

  def __getitem__(self, key):
    result = self._find_prefix(key)
    if result is None or result['match_weight'] == 0:
      raise KeyError('%s not in Trie' % key)
    return result['match_weight']

  def has_keys_with_prefix(self, prefix):
    return self._find_prefix(prefix) is not None

  def _find_prefix(self, prefix):
    l = len(prefix)
    pos = 0
    cursor = self._index
    while pos < l:
      target = prefix[pos]
      if target not in cursor:
        break
      cursor = cursor[target]
      pos += 1
    if pos == l:
      return cursor
    return None

  def magnitude(self):
    return self._largest

  def interesting_threshold(self):
    return self._percentile25

  def walk(self, seek_sets, exact_match=False):
    """Returns solutions matching `seek_sets`, ordered from high to low."""
    # TODO: Inline per findings from commit 47a736f.
    fringe = _MaxHeap()
    solutions = []
    acc = []
    fringe.push(float('inf'), (acc, self._index))
    stop_seek_pos = len(seek_sets) - 1
    seek_set_mode = isinstance(seek_sets, base_seek_set.BaseSeekSet)
    while len(fringe):
      fringe_score = fringe.best_weight()
      acc, cursor = fringe.pop()
      pos = len(acc)
      if seek_set_mode:
        seeking = seek_sets.seek(acc)
      else:
        seeking = seek_sets[pos]
      for c in seeking:
        if c not in cursor:
          continue
        acc.append(c)
        next_children = cursor[c]
        if not exact_match or pos == stop_seek_pos:
          match_weight = next_children['match_weight']
          if match_weight:
            heapq.heappush(solutions, (-match_weight, ''.join(acc)))
        if len(next_children) > 2 and pos < stop_seek_pos:
          if exact_match and stop_seek_pos >= next_children['max_length']:
            pass
          else:
            magnitude = next_children['max_weight']
            fringe.push(magnitude, (acc[:], next_children))
        acc.pop()
      while len(solutions) and -solutions[0][0] >= fringe_score:
        solution_weight, solution_word = heapq.heappop(solutions)
        yield solution_word, -solution_weight
    while len(solutions):
      solution_weight, solution_word = heapq.heappop(solutions)
      yield solution_word, -solution_weight

    if len(fringe._pool) > 15:
      print('WARNING')
      print('Max fringe size was: %s' % len(fringe._pool))

  def _add_to_index(self, word, weight):
    l = len(word)
    cursor = self._index
    if l > self._index['max_length']:
      self._index['max_length'] = l
    pos = 0
    while pos < l:
      target = word[pos]
      if target not in cursor:
        break
      cursor = cursor[target]
      match_weight = cursor['match_weight']
      if l > cursor['max_length']:
        cursor['max_length'] = l
      pos += 1
      if pos == l:
        if match_weight:
          # Duplicate addition.
          raise KeyError('%s already added' % word)
        # Exhausted input; this spells something now.
        cursor['match_weight'] = weight
        self._len += 1
        return
      elif len(cursor) <= 2:
        break  # End of Trie.
    # Add remaining characters.
    end = len(word) - 1
    for i in range(pos, len(word)):
      if i == end:
        cursor[word[i]] = {
          'max_weight': weight,
          'max_length': l,
          'match_weight': weight,
        }
      else:
        new_cursor = {
          'max_weight': weight,
          'max_length': l,
          'match_weight': 0,
        }
        cursor[word[i]] = new_cursor
        cursor = new_cursor
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

  def best_weight(self):
    return -self._heap[0][0]

  def pop(self):
    _, idx = heapq.heappop(self._heap)
    result = self._pool[idx]
    self._pool[idx] = None
    self._free_positions.append(idx)
    return result
