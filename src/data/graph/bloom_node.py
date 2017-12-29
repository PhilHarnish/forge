from typing import Dict, ItemsView, Iterable, Optional

from data.graph import _op_mixin, bloom_mask, bloom_node_reducer


class BloomNode(_op_mixin.OpMixin):
  """Graph node with bloom-filter style optimizations."""
  __slots__ = (
    'provide_mask',
    'require_mask',
    'lengths_mask',
    'max_weight',
    'match_weight',
    '_edges',
  )

  # Bloom filter for edge labels provided by descendants.
  provide_mask: int
  # Bloom filter for edge labels required by descendants.
  require_mask: int
  # Bloom filter for distances remaining until matching node.
  lengths_mask: int
  # Maximum match weight in descendant nodes.
  max_weight: float
  # Match value for this node.
  match_weight: float
  # Outgoing edges of this node.
  _edges: Dict[str, 'BloomNode']

  def __init__(self, op: Optional[_op_mixin.Op] = None) -> None:
    super(BloomNode, self).__init__(op)
    self.provide_mask = bloom_mask.PROVIDE_NOTHING
    self.require_mask = bloom_mask.REQUIRE_NOTHING
    self.lengths_mask = 0
    self.match_weight = 0
    self.max_weight = 0
    self._edges = {}

  def distance(self, length: int) -> None:
    """Report distance to a matching node."""
    self.lengths_mask |= 2 ** length

  def edges(self) -> Dict[str, 'BloomNode']:
    self._expand()
    return self._edges

  def items(self) -> ItemsView[str, 'BloomNode']:
    self._expand()
    yield from self._edges.items()

  def link(self, key: str, node: 'BloomNode') -> None:
    """Links `self` to `node` via `key`."""
    self._link(key, node, self._empty())

  def links(self, keys: Iterable[str], node: 'BloomNode') -> None:
    inherit = self._empty()
    for key in keys:
      self._link(key, node, inherit)

  def _link(self, key: str, node: 'BloomNode', inherit: bool) -> None:
    if key in self._edges:
      raise KeyError('Key "%s" already linked' % key)
    self._edges[key] = node
    if not inherit:
      return
    elif key in bloom_mask.SEPARATOR:
      return  # Prevent inheriting across word boundary characters.
    provide_mask = node.provide_mask
    if node.match_weight:
      # We cannot inherit requirements from a matching node; traversing edge
      # is a sufficient requirement.
      require_mask = bloom_mask.REQUIRE_NOTHING
    else:
      require_mask = node.require_mask
    try:
      edge_mask = bloom_mask.for_alpha(key)  # FIXME: This is inflexible.
      provide_mask |= edge_mask
      require_mask |= edge_mask
    except ValueError:
      pass
    self.provide_mask |= provide_mask
    self.require_mask &= require_mask
    # Inherit matching lengths (offset by 1).
    self.lengths_mask |= node.lengths_mask << 1
    if node.max_weight > self.max_weight:
      self.max_weight = node.max_weight

  def open(self, key: str) -> 'BloomNode':
    """Return outgoing edge `k`. Create node if necessary."""
    if key not in self._edges:
      child = self._find(key)
      if child is None:
        child = BloomNode()
      self._link(key, child, False)
    return self._edges[key]

  def require(self, mask: int) -> None:
    """Declare requirements for this node."""
    # Requirements become more sparse with time.
    self.require_mask &= mask
    # Anything a node requires is implicitly provided.
    # Provides become more numerous with time.
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
    if weight > self.max_weight:
      self.max_weight = weight

  def __len__(self) -> int:
    self._expand()
    return len(self._edges)

  def __contains__(self, key: str) -> bool:
    if key not in self._edges:
      child = self._find(key)
      if child is not None:
        self._link(key, child, self._empty())
    return key in self._edges

  def __getitem__(self, key: str) -> 'BloomNode':
    if key not in self._edges:
      child = self._find(key)
      if child is not None:
        self._link(key, child, self._empty())
    return self._edges[key]

  def __iter__(self) -> Iterable[str]:
    for k, v in self.items():
      yield k

  def _alloc(self, *args, **kwargs) -> 'BloomNode':
    return BloomNode(*args, **kwargs)

  def _empty(self) -> bool:
    return not (self.lengths_mask or self.provide_mask or self._edges)

  def _expand(self) -> None:
    if not self.op:
      return
    # Inherit from all child nodes only if empty before beginning.
    inherit = self._empty()
    for key, reduced in bloom_node_reducer.reduce(
        self.op, blacklist=self._edges):
      self._link(key, reduced, inherit)
    self.op = None  # No need to redo this work ever again.

  def _find(self, key: str) -> Optional['BloomNode']:
    """Returns common node for `k` from sources, if any."""
    if not self.op:
      return None
    for key, reduced in bloom_node_reducer.reduce(
        self.op, whitelist={key}):
      return reduced
    return None

  def __str__(self) -> str:
    self._expand()
    if self.lengths_mask:
      # Convert mask to binary, reverse, and swap "01" for " #"
      lengths = bin(self.lengths_mask)[:1:-1].replace(
          '0', ' ').replace('1', '#')
    else:
      lengths = ''
    return '%s(%s, %s, %s)' % (
        self.__class__.__name__,
        repr(bloom_mask.map_to_str(self.provide_mask, self.require_mask)),
        repr(lengths),
        self.match_weight)

  __repr__ = __str__
