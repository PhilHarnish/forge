import itertools
from typing import Container, ItemsView, List, Optional

from data import iter_util
from data.graph import _op_mixin, bloom_node


def reduce(
    op: _op_mixin.Op,
    whitelist: Container[str] = None,
    blacklist: Container[str] = None) -> ItemsView[str, 'bloom_node.BloomNode']:
  operands = op.operands()
  if not operands:
    return {}.items()
  iterator_fn, visitor_fn = _operator_functions[op.operator()]
  edges = []
  extra = []
  for operator in operands:
    if isinstance(operator, bloom_node.BloomNode):
      edges.append(operator.edges())
    else:
      extra.append(operator)
  for key, sources in iterator_fn(
      edges,
      whitelist=whitelist,
      blacklist=blacklist):
    result = visitor_fn(sources, extra)
    if result is not None:
      yield key, result


def _visit_identity(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> 'bloom_node.BloomNode':
  if not extra and len(sources) == 1:
    return sources[0]
  raise NotImplementedError(
      'OP_IDENTITY failed to reduce %s, %s' % (sources, extra))


def _visit_add(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> Optional['bloom_node.BloomNode']:
  if extra:
    raise NotImplementedError('OP_ADD failed to reduce %s' % extra)
  # Round up all of the values from all available sources.
  lengths_mask = sources[0].lengths_mask
  provide_mask = sources[0].provide_mask
  require_mask = sources[0].require_mask
  pos = 1
  l = len(sources)
  while pos < l:
    source = sources[pos]
    lengths_mask |= source.lengths_mask  # Lengths from either are provided.
    provide_mask |= source.provide_mask  # Letters from either are provided.
    require_mask &= source.require_mask  # Requirements are reduced.
    pos += 1
  reduced = bloom_node.BloomNode(_op_mixin.Op(_op_mixin.OP_ADD, sources))
  reduced.provide_mask = provide_mask
  reduced.require_mask = require_mask
  reduced.lengths_mask = lengths_mask
  reduced.max_weight = max(source.max_weight for source in sources)
  reduced.match_weight = max(source.match_weight for source in sources)
  return reduced


def _visit_multiply(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> Optional['bloom_node.BloomNode']:
  scale = 1
  for n in extra:
    scale *= n
  # First, verify there are matching masks. It's required for a valid
  # solution and is trivial to verify satisfaction.
  lengths_mask = sources[0].lengths_mask
  provide_mask = sources[0].provide_mask
  require_mask = sources[0].require_mask
  match_weight = sources[0].match_weight * scale
  max_weight = sources[0].max_weight
  pos = 1
  l = len(sources)
  while pos < l and lengths_mask and (
      not require_mask or (provide_mask & require_mask) == require_mask):
    source = sources[pos]
    lengths_mask &= source.lengths_mask  # Overlapping solution lengths exist.
    provide_mask &= source.provide_mask  # Overlapping letters are provided.
    require_mask |= source.require_mask  # Requirements are combined.
    max_weight *= source.max_weight  # Trends to 0.
    match_weight *= source.match_weight
    pos += 1
  if (not lengths_mask or
      (require_mask and (provide_mask & require_mask) != require_mask) or
      not max_weight):
    return None  # Unsatisfiable; no common requirements.
  # Verify all combinations are mutually satisfiable.
  for a, b in itertools.combinations(sources, 2):
    if not a.satisfies(b) or not b.satisfies(a):
      return None
  reduced = bloom_node.BloomNode(_op_mixin.Op(_op_mixin.OP_MULTIPLY, sources))
  reduced.provide_mask = provide_mask
  reduced.require_mask = require_mask
  reduced.lengths_mask = lengths_mask
  reduced.max_weight = max_weight
  reduced.match_weight = match_weight
  return reduced


_operator_functions = [
  (iter_util.common, _visit_identity),
  (iter_util.both, _visit_add),
  (iter_util.common, _visit_multiply),
]
