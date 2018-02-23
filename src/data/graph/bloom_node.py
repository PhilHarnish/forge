import collections
from typing import Any, Dict, ItemsView, Iterable, Optional

from data.convert import repr_format
from data.graph import _op_mixin, bloom_mask, bloom_node_reducer


class BloomNode(_op_mixin.OpMixin):
  """Graph node with bloom-filter style optimizations."""
  __slots__ = (
    'provide_mask',
    'require_mask',
    'lengths_mask',
    'max_weight',
    'match_weight',
    '_annotations',
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
  # Annotations on this node.
  _annotations: Dict[str, Any]
  # Outgoing edges of this node.
  _edges: Dict[str, 'BloomNode']

  def __init__(self, op: Optional[_op_mixin.Op] = None) -> None:
    super(BloomNode, self).__init__(op)
    self.provide_mask = bloom_mask.PROVIDE_NOTHING
    self.require_mask = bloom_mask.REQUIRE_NOTHING
    self.lengths_mask = 0
    self.match_weight = 0
    self.max_weight = 0
    self._annotations = None
    self._edges = {}

  def distance(self, length: int) -> None:
    """Report distance to a matching node."""
    self.lengths_mask |= 1 << length

  def edges(self, readonly=False) -> Dict[str, 'BloomNode']:
    if not readonly:
      self._expand()
    return self._edges

  def items(self) -> ItemsView[str, 'BloomNode']:
    self._expand()
    yield from self._edges.items()

  def link(self, key: str, node: 'BloomNode') -> None:
    """Links `self` to `node` via `key`."""
    self._link(key, node, True)

  def links(self, keys: Iterable[str], node: 'BloomNode') -> None:
    for key in keys:
      self._link(key, node, True)

  def _link(self, key: str, node: 'BloomNode', inherit: bool) -> None:
    if key in self._edges:
      raise KeyError('Key "%s" already linked' % key)
    self._edges[key] = node
    if not inherit:
      return
    edge_mask = bloom_mask.for_alpha(key)
    self.provide_mask |= edge_mask
    require_edge_mask = edge_mask
    if key == bloom_mask.WORD_SEPARATOR:
      # Prevent inheriting across word boundary characters.
      # Additionally, this node is (apparently) terminal and doesn't require
      # any additional characters (aside from perhaps space itself).
      self.require_mask &= require_edge_mask
      return
    if node.op:
      bloom_node_reducer.merge(node)
    self.provide_mask |= node.provide_mask
    if node.match_weight:
      # We cannot inherit requirements from a matching node; traversing edge
      # is a sufficient requirement.
      require_child_mask = bloom_mask.REQUIRE_NOTHING
    else:
      require_child_mask = node.require_mask
    self.require_mask &= require_edge_mask | require_child_mask
    # Inherit matching lengths (offset by 1).
    self.lengths_mask |= node.lengths_mask << 1
    if node.max_weight > self.max_weight:
      self.max_weight = node.max_weight

  def annotate(
      self, new_annotations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if new_annotations is not None:
      if self._annotations is None:
        self._annotations = collections.defaultdict(_AnnotationValue)
      for key, value in new_annotations.items():
        self._annotations[key].add(value)
    return self._annotations

  def annotations(self) -> Dict[str, Any]:
    if self.op:
      bloom_node_reducer.merge(self)
    return self._annotations

  def open(self, key: str) -> 'BloomNode':
    """Return outgoing edge `k`. Create node if necessary."""
    if key not in self._edges:
      child = self._find(key)
      if child is None:
        child = self._alloc()
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
        self._link(key, child, True)
    return key in self._edges

  def __getitem__(self, key: str) -> 'BloomNode':
    if key not in self._edges:
      child = self._find(key)
      if child is not None:
        self._link(key, child, True)
    return self._edges[key]

  def __iter__(self) -> Iterable[str]:
    for k, v in self.items():
      yield k

  def _expand(self) -> None:
    if self.op is None:
      return
    for key, reduced in bloom_node_reducer.reduce(self, blacklist=self._edges):
      self._link(key, reduced, True)
    self.op = None  # No need to redo this work ever again.

  def _find(self, key: str) -> Optional['BloomNode']:
    """Returns common node for `k` from sources, if any."""
    if not self.op:
      return None
    for key, reduced in bloom_node_reducer.reduce(self, whitelist={key}):
      return reduced
    return None

  def __repr__(self) -> str:
    self._expand()
    return str(self)

  def __str__(self) -> str:
    args = [repr(bloom_mask.map_to_str(self.provide_mask, self.require_mask))]
    if self.lengths_mask:
      # Convert mask to binary, reverse, and swap "01" for " #"
      lengths = bin(self.lengths_mask)[:1:-1].replace(
          '0', ' ').replace('1', '#')
    else:
      lengths = ''
    args.append(repr(lengths))
    weight = str(self.match_weight)
    if weight.endswith('.0'):
      weight = weight[:-2]
    args.append(weight)
    if self._annotations:
      args.append(repr_format.as_args(**self._annotations))
    return '%s(%s)' % (
        self.__class__.__name__,
        ', '.join(args))

# Wire "_alloc" directly to constructor.
setattr(BloomNode, '_alloc', BloomNode)


class _AnnotationValue(set):
  def add(self, element: Any):
    if isinstance(element, _AnnotationValue):
      self.update(element)
    else:
      super(_AnnotationValue, self).add(element)

  def __repr__(self) -> str:
    if not self:
      return 'None'
    elif len(self) > 1:
      return '{%s}' % ', '.join(map(repr, sorted(self, key=repr)))
    return repr(next(iter(self)))

  __str__ = __repr__
