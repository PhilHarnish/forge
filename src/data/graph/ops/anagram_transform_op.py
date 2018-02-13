from typing import Callable, Collection, Iterable, List, Union

from data.anagram import anagram_iter
from data.graph import _op_mixin, bloom_mask, bloom_node, bloom_node_reducer

Transformer = Callable[['bloom_node.BloomNode'], 'bloom_node.BloomNode']


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
  children = list(state)
  # TODO: Need a cleaner way to inject and rerun these nodes.
  if len(children) == 1:
    host.op = _op_mixin.Op(_op_mixin.OP_IDENTITY, children)
  else:
    host.op = _op_mixin.Op(_op_mixin.OP_ADD, children)
  # HACK: This duplicates BloomNode._expand, essentially.
  for key, reduced in bloom_node_reducer.reduce(
      host, whitelist=whitelist, blacklist=blacklist):
    host.link(key, reduced)


class _AnagramTransformIndex(object):
  """Singleton object used during anagram traversal."""
  def __init__(
      self,
      exit_node: 'bloom_node.BloomNode',
      root: anagram_iter.AnagramIter) -> None:
    self._exit_node = exit_node
    reference = bloom_node.BloomNode()
    reference.distance(0)
    reference.weight(1, True)
    reference_choice_paths = {}
    for choice, _ in root.available():
      reference_choice_paths[choice] = choice(reference)
    self._reference_choice_paths = reference_choice_paths
    self._child_cache = {}

  def iter(
      self,
      anagrams: anagram_iter.AnagramIter,
  ) -> Iterable['bloom_node.BloomNode']:
    for child_choice, child_anagrams in anagrams.items():
      key = (child_choice, child_anagrams)
      if key not in self._child_cache:
        self._child_cache[key] = self._make_child(child_choice, child_anagrams)
      yield self._child_cache[key]

  def _make_child(
      self,
      choice: Transformer,
      anagrams: anagram_iter.AnagramIter) -> 'bloom_node.BloomNode':
    children = list(anagrams.available())
    if not children:
      return choice(self._exit_node)
    elif len(children) == 1:
      child_choice, child_duplicates = children[0]
      node = self._exit_node
      while child_duplicates:
        node = child_choice(node)
        child_duplicates -= 1
      return choice(node)
    # Compute requirements from exits.
    node = self._exit_node // _AnagramState(self, anagrams)
    node.provide_mask = self._exit_node.provide_mask
    node.require_mask = self._exit_node.require_mask
    node.lengths_mask = self._exit_node.lengths_mask
    node.annotations({'anagrams': anagrams})
    node.max_weight = self._exit_node.max_weight
    for child_choice, child_duplicates in children:
      path = self._reference_choice_paths[child_choice]
      node.provide_mask |= path.provide_mask
      node.require_mask |= path.require_mask
      node.lengths_mask = bloom_mask.lengths_product(
          node.lengths_mask, path.lengths_mask, duplicates=child_duplicates)
      # TODO: Check for whitespace.
    return choice(node)


class _AnagramState(object):
  def __init__(
      self,
      index: _AnagramTransformIndex,
      anagrams: anagram_iter.AnagramIter):
    self._index = index
    self._anagrams = anagrams

  def __iter__(self) -> Iterable['bloom_node.BloomNode']:
    yield from self._index.iter(self._anagrams)

  def __repr__(self) -> str:
    return '_AnagramState(%s)' % self._anagrams

  __str__ = __repr__


def _normalize_state(
    exit_node: 'bloom_node.BloomNode',
    index: Union[Iterable, anagram_iter.AnagramIter]) -> _AnagramState:
  if isinstance(index, _AnagramState):
    return index
  # `index` is an iterable list of ???, one-by-one these will be taken as a
  # route to the `exit_node`.
  initial_anagrams = anagram_iter.from_choices(index)
  index = _AnagramTransformIndex(exit_node, initial_anagrams)
  return _AnagramState(index, initial_anagrams)
