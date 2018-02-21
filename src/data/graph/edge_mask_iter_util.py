from typing import Iterable, List, Optional, Tuple, TypeVar

from data.graph import bloom_mask, bloom_node

_POW_MAP = {
  1 << i: i for i in range(bloom_mask.SIZE)
}
T = TypeVar('T')  # Generic type.


def iterable_both(
    nodes: List['bloom_node.BloomNode'],
    whitelist: Optional[int] = bloom_mask.REQUIRE_NOTHING,
    blacklist: Optional[int] = 0,
) -> Iterable[Tuple[str, List[T]]]:
  if blacklist:
    skip_bits = blacklist
  else:
    skip_bits = 0
  node_edges = [(n, n.edge_list()) for n in nodes]
  for pos, node in enumerate(nodes):
    active_mask = node.edge_mask
    active_mask -= active_mask & skip_bits
    for bit in bloom_mask.bits(active_mask & whitelist):
      index = _POW_MAP[bit]
      yield bloom_mask.ALPHA_CHARACTERS[index], [
        edges[index] for n, edges in node_edges[pos:] if n.edge_mask & bit
      ]
    skip_bits |= active_mask


def iterable_common(
    nodes: List['bloom_node.BloomNode'],
    whitelist: Optional[int] = None,
    blacklist: Optional[int] = None,
) -> Iterable[Tuple[str, List[T]]]:
  if whitelist is None:
    matched = bloom_mask.REQUIRE_NOTHING
  else:
    matched = whitelist
  edges = [n.edge_list() for n in nodes]
  for node in nodes:
    matched &= node.edge_mask
  if blacklist is not None:
    matched -= matched & blacklist
  for index in bloom_mask.indexes(matched):
    yield bloom_mask.ALPHA_CHARACTERS[index], [
      e[index] for e in edges
    ]
