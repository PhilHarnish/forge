from typing import Collection, ItemsView, Iterable, List, Union

from data.anagram import anagram_set
from data.graph import bloom_mask, bloom_node

_SPACE_MASK = bloom_mask.for_alpha(' ')


def merge_fn(
    host: 'bloom_node.BloomNode',
    sources: List['bloom_node.BloomNode'],
    extra: list,
    whitelist: Collection = None,
    blacklist: Collection = None,
    **kwargs) -> None:
  del kwargs
  assert len(sources) == 1
  exit_node = sources[0]
  assert len(extra) == 1
  state = _normalize_state(exit_node, extra[0])
  for key, node in state.items(whitelist=whitelist, blacklist=blacklist):
    # HACK: Hide the operator from node so that expanding is cheap.
    op = node.op
    node.op = None
    host.link(key, node)
    node.op = op


class _AnagramIndex(object):
  """Singleton object used during anagram traversal."""
  def __init__(
      self,
      exit_node: 'bloom_node.BloomNode',
      root: anagram_set.AnagramSet) -> None:
    self._exit_node = exit_node
    mask_cache = {}
    for choice in root.choices():
      if choice not in mask_cache:
        anagram_mask = 0
        for c in choice:
          anagram_mask |= bloom_mask.for_alpha(c)
        mask_cache[choice] = anagram_mask
    self._mask_cache = mask_cache
    self._state_cache = {}

  def items(
      self,
      anagrams: anagram_set.AnagramSet,
      whitelist: Collection,
      blacklist: Collection,
  ) -> ItemsView[str, 'bloom_node.BloomNode']:
    exit_require_mask = self._exit_node.require_mask
    exit_provide_mask = self._exit_node.provide_mask
    exit_lengths_mask = self._exit_node.lengths_mask
    exit_max_weight = self._exit_node.max_weight
    for child_choice, child_anagrams in anagrams.items():
      if whitelist and child_choice not in whitelist:
        continue
      elif blacklist and child_choice in blacklist:
        continue
      # Inherit requirements from exit.
      node_mask = 0
      exit_distance = 0
      has_space = False
      for available_choice in child_anagrams.choices():
        choice_length = len(available_choice)
        exit_distance += choice_length
        if available_choice not in self._mask_cache:
          choice_mask = 0
          for c in available_choice:
            choice_mask |= bloom_mask.for_alpha(c)
          self._mask_cache[available_choice] = choice_mask
        node_mask |= self._mask_cache[available_choice]
        has_space |= available_choice in bloom_mask.SEPARATOR
      if exit_distance:
        node = self._exit_node / _AnagramState(self, child_anagrams)
        node.provide_mask = exit_provide_mask | node_mask
        if has_space:
          # Space is the only REALLY required character. Others are optional.
          node.require_mask = _SPACE_MASK
          # Assume it's possible to make words in [0 .. exit_distance - 1].
          node.lengths_mask = (1 << (exit_distance - 1)) - 1
        else:
          node.require_mask = exit_require_mask | node_mask
          node.lengths_mask = exit_lengths_mask << exit_distance
        node.max_weight = exit_max_weight
      else:
        node = self._exit_node
      yield child_choice, node


class _AnagramState(object):
  def __init__(self, index: _AnagramIndex, anagrams: anagram_set.AnagramSet):
    self._index = index
    self._anagrams = anagrams

  def items(
      self,
      whitelist: Collection,
      blacklist: Collection) -> ItemsView[str, 'bloom_node.BloomNode']:
    yield from self._index.items(self._anagrams, whitelist, blacklist)


def _normalize_state(
    exit_node: 'bloom_node.BloomNode',
    index: Union[Iterable, anagram_set.AnagramSet]) -> _AnagramState:
  if isinstance(index, _AnagramState):
    return index
  initial_anagrams = anagram_set.from_choices(index)
  index = _AnagramIndex(exit_node, initial_anagrams)
  return _AnagramState(index, initial_anagrams)
