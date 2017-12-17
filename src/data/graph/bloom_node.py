from typing import Dict, Optional


class BloomNode(object):
  """Graph node with bloom-filter style optimizations."""
  __slots__ = (
    'provide_mask',
    'require_mask',
    'lengths_mask',
    'max_weight',
    'min_weight',
    'match_weight',
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
  # Outgoing edges of this node.
  _edges: Dict[str, 'BloomNode']

  def __init__(self) -> None:
    self.provide_mask = None
    self.require_mask = None
    self.lengths_mask = None
    self.match_weight = 0
    self.max_weight = 0
    self.min_weight = 0
    self._edges = {}

  def distance(self, length: int) -> None:
    """Report distance to a matching node."""
    mask = 2 ** length
    if self.lengths_mask is None:
      self.lengths_mask = mask
    else:
      self.lengths_mask |= mask

  def open(self, k: str) -> 'BloomNode':
    """Return outgoing edge `k`. Create node if necessary."""
    if k not in self._edges:
      self._edges[k] = BloomNode()
    return self._edges[k]

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
    return len(self._edges)

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
