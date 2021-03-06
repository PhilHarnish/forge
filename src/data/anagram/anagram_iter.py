from typing import ItemsView, Iterable, List, Optional, TypeVar

from data.graph import bloom_mask

T = TypeVar('T')  # Generic type.


class _AnagramIterIndex(object):
  def __init__(self, choices: List[T]) -> None:
    num_choices = len(choices)
    assert num_choices < 63
    self._choice_map = {}
    self._choices = {}
    self._choices_masks = {}
    self._initial_choice_mask = 0
    last_choice = None
    idx = None
    for i, choice in enumerate(sorted(choices, key=id)):
      if last_choice == choice:
        continue
      last_choice = choice
      if idx is not None:
        # 0b01100 = (0b10000 - 1) - (0b00100 - 1)
        # 0b01100 =  0b01111      -  0b00011
        self._choices_masks[idx] = ((1 << i) - 1) - (idx - 1)
      idx = 1 << i
      self._choice_map[choice] = idx
      self._choices[idx] = choice
      self._initial_choice_mask |= idx
    if idx is not None:
      self._choices_masks[idx] = ((1 << num_choices) - 1) - (idx - 1)
    self._child_cache = {}
    self.initial_available = (1 << num_choices) - 1

  def iter(self, available: int) -> Iterable[T]:
    # Only iterate through IDs which align with initial choice mask.
    for candidate in bloom_mask.bits(available & self._initial_choice_mask):
      yield self._choices[candidate]

  def get(self, available: int, item: T) -> 'AnagramIter':
    idx = self._choice_map[item]
    mask = self._choices_masks[idx]
    match = available & mask
    if not match:
      raise KeyError(item)
    available -= (match ^ (match >> 1)) & mask
    return self._get(available)

  def _get(self, available: int) -> 'AnagramIter':
    if available not in self._child_cache:
      self._child_cache[available] = AnagramIter(self, available)
    return self._child_cache[available]

  def items(self, available: int) -> ItemsView[T, 'AnagramIter']:
    # Only iterate through IDs which align with initial choice mask.
    for idx in bloom_mask.bits(available & self._initial_choice_mask):
      mask = self._choices_masks[idx]
      match = available & mask
      child_available = available - ((match ^ (match >> 1)) & mask)
      yield self._choices[idx], self._get(child_available)

  def available(self, available: int) -> ItemsView[T, int]:
    # Only iterate through IDs which align with initial choice mask.
    for idx in bloom_mask.bits(available & self._initial_choice_mask):
      duplicates = len(
          list(bloom_mask.bits(available & self._choices_masks[idx])))
      yield self._choices[idx], duplicates


class AnagramIter(object):
  __slots__ = ('_index', '_available')

  def __init__(
      self,
      index: _AnagramIterIndex,
      available: Optional[int] = None) -> None:
    self._index = index
    if available is None:
      self._available = index.initial_available
    else:
      self._available = available

  def items(self) -> ItemsView[T, 'AnagramIter']:
    yield from self._index.items(self._available)

  def available(self) -> ItemsView[T, int]:
    """Optimized path for listing each option as though it were the last."""
    yield from self._index.available(self._available)

  def __iter__(self) -> Iterable[T]:
    yield from self._index.iter(self._available)

  def __getitem__(self, item: T) -> 'AnagramIter':
    return self._index.get(self._available, item)

  def __repr__(self) -> str:
    available = []
    for value, duplicates in self.available():
      if duplicates > 1:
        available.append('%s*%s' % (value, duplicates))
      else:
        available.append(str(value))
    return '%s(%s)' % (
      self.__class__.__name__,
      ', '.join(sorted(available)),
    )

  __str__ = __repr__


def from_choices(choices: Iterable[T]) -> AnagramIter:
  if not isinstance(choices, list):
    choices = list(choices)
  return AnagramIter(_AnagramIterIndex(choices))
