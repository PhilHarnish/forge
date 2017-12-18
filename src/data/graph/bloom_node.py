import itertools
from typing import Dict, Iterable, List, Optional


class BloomNode(object):
  """Graph node with bloom-filter style optimizations."""
  __slots__ = (
    'provide_mask',
    'require_mask',
    'lengths_mask',
    'max_weight',
    'min_weight',
    'match_weight',
    '_sources',
    '_edges',
  )

  # Bloom filter for edge labels provided by descendants.
  provide_mask: Optional[int]
  # Bloom filter for edge labels required by descendants.
  require_mask: Optional[int]
  # Bloom filter for distances remaining until matching node.
  lengths_mask: Optional[int]
  # Maximum match weight in descendant nodes.
  max_weight: float
  # Minimum match weight in descendant nodes.
  min_weight: float
  # Match value for this node.
  match_weight: float
  # Input sources for this node.
  _sources: Optional[Iterable['BloomNode']]
  # Outgoing edges of this node.
  _edges: Dict[str, 'BloomNode']

  def __init__(self, sources: Optional[Iterable['BloomNode']] = None) -> None:
    self.provide_mask = None
    self.require_mask = None
    self.lengths_mask = None
    self.match_weight = 0
    self.max_weight = 0
    self.min_weight = 0
    self._sources = sources
    self._edges = {}

  def distance(self, length: int) -> None:
    """Report distance to a matching node."""
    mask = 2 ** length
    if self.lengths_mask is None:
      self.lengths_mask = mask
    else:
      self.lengths_mask |= mask

  def open(self, key: str) -> 'BloomNode':
    """Return outgoing edge `k`. Create node if necessary."""
    if key not in self._edges:
      child = self._find(key)
      if child is None:
        self._edges[key] = BloomNode()
      else:
        self._edges[key] = child
    return self._edges[key]

  def require(self, mask: int) -> None:
    """Declare requirements for this node."""
    if self.require_mask is None:
      self.require_mask = mask
    else:
      # Requirements become more sparse with time.
      self.require_mask &= mask
    if self.provide_mask is None:
      self.provide_mask = mask
    else:
      # Anything a node requires is implicitly provided.
      self.provide_mask |= mask

  def satisfies(self, other: 'BloomNode') -> bool:
    return other.require_mask & self.provide_mask == other.require_mask

  def weight(self, weight: float, match: bool = False) -> None:
    """Assign weight to this node, optionally specifying a match here."""
    if match:
      if self.match_weight:
        raise ValueError(
            '%s already has match weight %s' % (self, self.match_weight))
      self.match_weight = weight
    self.max_weight = max(weight, self.max_weight)
    self.min_weight = max(weight, self.min_weight)

  def __len__(self) -> int:
    # TODO: Need to expand edges first.
    return len(self._edges)

  def __contains__(self, key: str) -> bool:
    if key not in self._edges:
      child = self._find(key)
      if child is not None:
        self._edges[key] = child
    return key in self._edges

  def __getitem__(self, key: str) -> 'BloomNode':
    if key not in self._edges:
      child = self._find(key)
      if child is not None:
        self._edges[key] = child
    return self._edges[key]

  def _find(self, key: str) -> Optional['BloomNode']:
    """Returns common node for `k` from sources, if any."""
    if not self._sources:
      return None
    sources = []
    for source in self._sources:
      if key not in source:
        return None
      sources.append(source[key])
    return reduce(sources)

  def __repr__(self) -> str:
    chars = []
    for i in range(26):
      if self.require_mask and self.require_mask & (2 ** i):
        chars.append(chr(ord('A') + i))
      elif self.require_mask and self.provide_mask & (2 ** i):
        chars.append(chr(ord('a') + i))
    if self.lengths_mask:
      # Convert mask to binary, reverse, and swap "01" for " #"
      lengths = bin(self.lengths_mask)[:1:-1].replace(
          '0', ' ').replace('1', '#')
    else:
      lengths = ''
    return '%s(%s, %s, %s)' % (
        self.__class__.__name__, repr(''.join(chars)), repr(lengths),
        self.match_weight)


def reduce(sources: List['BloomNode']) -> Optional['BloomNode']:
  if not sources or any(
          not source.lengths_mask or
          not source.provide_mask or
          not source.max_weight or
          source.require_mask is None
              for source in sources):
    return None
  # First, verify there are matching masks. It's required for a valid
  # solution and is trivial to verify satisfaction.
  lengths_mask = sources[0].lengths_mask
  provide_mask = sources[0].provide_mask
  require_mask = sources[0].require_mask
  match_weight = sources[0].match_weight
  min_weight = sources[0].min_weight
  max_weight = sources[0].max_weight
  pos = 1
  l = len(sources)
  while pos < l and lengths_mask and (
        provide_mask & require_mask) == require_mask:
    source = sources[pos]
    lengths_mask &= source.lengths_mask  # Overlapping solution lengths exist.
    provide_mask &= source.provide_mask  # Overlapping letters are provided.
    require_mask |= source.require_mask  # Requirements are combined.
    min_weight = min(min_weight, source.min_weight)
    max_weight = min(max_weight, source.max_weight)
    match_weight = min(match_weight, source.match_weight)  # Trends to 0.
    pos += 1
  if (not lengths_mask or
      (provide_mask & require_mask) != require_mask or
      not max_weight):
    return None  # Unsatisfiable; no common requirements.
  # Verify all combinations are mutually satisfiable.
  for a, b in itertools.combinations(sources, 2):
    if not a.satisfies(b) or not b.satisfies(a):
      return None
  reduced = BloomNode(sources)
  reduced.provide_mask = provide_mask
  reduced.require_mask = require_mask
  reduced.lengths_mask = lengths_mask
  reduced.min_weight = min_weight
  reduced.max_weight = max_weight
  reduced.match_weight = match_weight
  return reduced