import collections
import heapq
from typing import Iterable, List, Optional, Set, Tuple


class _AnagramIndex(object):
  def __init__(self, choices: List[str]) -> None:
    assert len(choices) < 63
    self._choices = {}
    self._choices_char_map = collections.defaultdict(int)
    for i, choice in enumerate(choices):
      idx = 1 << i
      self._choices[idx] = choice
      self._choices_char_map[choice[0]] |= idx
    self._child_cache = {}
    self.initial_available = (1 << len(choices)) - 1
    self._initial_choices = set(c[0] for c in choices)

  def available(self, available: int, prefix: str) -> Iterable[str]:
    if available == self.initial_available and not prefix:
      # Optimized path for first query.
      return self._initial_choices
    result = set()
    if prefix:
      self._populate_available_with_prefix(result, available, prefix)
    else:
      # Optimized path when there isn't a prefix.
      self._populate_available_without_prefix(result, available)
    return result

  def choices(self, available: int) -> List['str']:
    return [self._choices[i] for i in _ids(available)]

  def get(self, available: int, prefix: str) -> Optional['AnagramSet']:
    available, prefix = self._seek(available, prefix)
    return self._get(available, prefix)

  def _populate_available_without_prefix(
      self, result: Set[str], available: int) -> None:
    for candidate in _ids(available):
      result.add(self._choices[candidate][0])

  def _populate_available_with_prefix(
      self, result: Set[str], available: int, prefix: str) -> None:
    raise NotImplementedError()

  def _seek(self, available: int, prefix: str) -> Tuple[int, str]:
    for c in prefix:
      if not available:
        raise KeyError(prefix)
      candidates = available & self._choices_char_map[c]
      if not candidates:
        raise KeyError(prefix)
      # Remove lowest candidate from those available.
      available ^= candidates - (candidates & (candidates - 1))
    if not available:
      raise KeyError(prefix)
    return available, ''

  def _get(self, available: int, prefix: str) -> 'AnagramSet':
    key = '%s%s' % (available, prefix)
    if key not in self._child_cache:
      self._child_cache[key] = AnagramSet(self, available, prefix)
    return self._child_cache[key]


class _CompoundAnagramIndex(_AnagramIndex):
  def __init__(self, choices: List[str]) -> None:
    super(_CompoundAnagramIndex, self).__init__(choices)

  def _populate_available_with_prefix(
      self, result: Set[str], available: int, prefix: str) -> None:
    self._add_available(result, available, prefix, 0)

  def _add_available(
      self, result: Set[str], available: int, prefix: str, pos: int):
    prefix_length = len(prefix)
    c = prefix[pos]
    candidates = available & self._choices_char_map[c]
    for candidate in _ids(candidates):
      choice = self._choices[candidate]
      if not _match_suffix(prefix, pos, choice):
        continue
      choice_length = len(choice)
      next_pos = pos + choice_length
      next_available = available ^ candidate
      if next_pos > prefix_length:
        result.add(choice[prefix_length - pos])
      elif next_pos < prefix_length:
        self._add_available(result, next_available, prefix, next_pos)
      else:
        self._populate_available_without_prefix(result, next_available)

  def _seek(self, available: int, prefix: str) -> Tuple[int, str]:
    queue = [(0, available)]
    prefix_length = len(prefix)
    while queue and queue[0][0] < prefix_length:
      next_pos, next_available = heapq.heappop(queue)
      for exit_pos, exit_available in self._advance(
          next_available, prefix, next_pos):
        # Note: It is possible to detect bottlenecks mid-iteration but this
        # code assumes access happens one letter at a time. Bottleneck
        # optimization only happens at the end.
        heapq.heappush(queue, (exit_pos, exit_available))
    if not queue:
      raise KeyError(prefix)
    exit_pos, exit_available = queue[0]
    if len(queue) == 1 and exit_pos == prefix_length:
      # Solution was unique and perfectly spans prefix. Compact result.
      return exit_available, ''
    # Solution is not unique.
    return available, prefix

  def _advance(
      self, available: int, prefix: str, pos: int) -> Iterable[Tuple[int, int]]:
    c = prefix[pos]
    candidates = available & self._choices_char_map[c]
    options = []
    visited = set()
    for candidate in _ids(candidates):
      choice = self._choices[candidate]
      if choice in visited:
        continue
      visited.add(choice)
      if not _match_suffix(prefix, pos, choice):
        continue
      options.append((pos + len(choice), available ^ candidate))
    return options


class AnagramSet(object):
  __slots__ = ('_index', '_available', '_prefix')

  def __init__(
      self,
      index: _AnagramIndex,
      available: Optional[int] = None,
      prefix: Optional[str] = None) -> None:
    self._index = index
    if available is None:
      self._available = index.initial_available
    else:
      self._available = available
    if prefix is None:
      self._prefix = ''
    else:
      self._prefix = prefix

  def choices(self) -> List[str]:
    return self._index.choices(self._available)

  def __iter__(self) -> Iterable[str]:
    yield from self._index.available(self._available, self._prefix)

  def __getitem__(self, item: str) -> 'AnagramSet':
    return self._index.get(self._available, self._prefix + item)

  def __repr__(self) -> str:
    return '%s(%s, %s)' % (
      self.__class__.__name__,
      repr(self._index.choices(self._available)),
      repr(self._prefix),
    )

  __str__ = __repr__


def from_choices(choices: Iterable[str]) -> AnagramSet:
  if not isinstance(choices, list):
    choices = list(choices)
  if all(len(choice) == 1 for choice in choices):
    index = _AnagramIndex(choices)
  else:
    index = _CompoundAnagramIndex(choices)
  return AnagramSet(index)


def _ids(available: int) -> Iterable[int]:
  while available:
    next_available = available & (available - 1)
    lowest_choice = available - next_available
    yield lowest_choice
    available = next_available


def _match_suffix(reference:str, start:int, comparison: str) -> bool:
  """Skips the first character and compares the rest of comparison."""
  reference_length = len(reference)
  comparison_length = min(len(comparison), reference_length - start)
  reference_position = start + 1
  comparison_position = 1
  while comparison_position < comparison_length:
    if comparison[comparison_position] != reference[reference_position]:
      return False
    comparison_position += 1
    reference_position += 1
  return True
