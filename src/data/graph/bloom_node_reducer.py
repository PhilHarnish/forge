import itertools
from typing import Container, ItemsView, List, Optional, Tuple

from data import iter_util
from data.graph import _op_mixin, bloom_mask, bloom_node, edge_mask_iter_util
from data.graph.ops import anagram_op, anagram_transform_op

reduce = bloom_mask.everything.child('reduce')


def merge(host: 'bloom_node.BloomNode') -> None:
  op = host.op
  _, _, merge_fn, _ = _operator_functions[op.operator()]
  operands = op.operands()
  if not operands:
    return
  nodes = []
  extra = []
  for operator in operands:
    if isinstance(operator, bloom_node.BloomNode):
      nodes.append(operator)
    else:
      extra.append(operator)
  merge_fn(
      host, nodes, extra, whitelist=None, blacklist=host.edges(readonly=True),
      blacklist_mask=host.edge_mask,
  )


@reduce.profile('dict')
def reduce(
    host: 'bloom_node.BloomNode',
    whitelist: Container[str] = None,
    blacklist: Container[str] = None,
    whitelist_mask: int = bloom_mask.REQUIRE_NOTHING,
    blacklist_mask: int = 0) -> ItemsView[str, 'bloom_node.BloomNode']:
  op = host.op
  operands = op.operands()
  if not operands:
    return {}.items()
  nodes = []
  edges = []
  extra = []
  for operator in operands:
    if isinstance(operator, bloom_node.BloomNode):
      nodes.append(operator)
      edges.append(operator.edges())
    else:
      extra.append(operator)
  _, iterator_fn, merge_fn, visitor_fn = _operator_functions[op.operator()]
  for key, sources in iterator_fn(
      edges,
      whitelist=whitelist,
      blacklist=blacklist):
    result = visitor_fn(sources, extra)
    if result is not None:
      yield key, result
  # Merge must run after visit: visit will add host's outgoing edges and set
  # mask properties which merge expects to be present.
  merge_fn(
      host, nodes, extra, whitelist=whitelist, blacklist=blacklist,
      whitelist_mask=whitelist_mask, blacklist_mask=blacklist_mask)


@reduce.profile('list')
def reduce(
    host: 'bloom_node.BloomNode',
    whitelist: Container[str] = None,
    blacklist: Container[str] = None,
    whitelist_mask: int = bloom_mask.REQUIRE_NOTHING,
    blacklist_mask: int = 0) -> ItemsView[str, 'bloom_node.BloomNode']:
  op = host.op
  operands = op.operands()
  if not operands:
    return {}.items()
  nodes = []
  extra = []
  for operator in operands:
    if hasattr(operator, 'edge_mask'):
      nodes.append(operator)
    else:
      extra.append(operator)
  iterator_fn, _, merge_fn, visitor_fn = _operator_functions[op.operator()]
  for key, sources in iterator_fn(
      nodes,
      whitelist=whitelist_mask,
      blacklist=blacklist_mask):
    result = visitor_fn(sources, extra)
    if result is not None:
      yield key, result
  # Merge must run after visit: visit will add host's outgoing edges and set
  # mask properties which merge expects to be present.
  merge_fn(
      host, nodes, extra, whitelist=whitelist, blacklist=blacklist,
      whitelist_mask=whitelist_mask, blacklist_mask=blacklist_mask)


def _merge_add(
    host: 'bloom_node.BloomNode',
    sources: List['bloom_node.BloomNode'],
    extra: list,
    **kwargs) -> None:
  del kwargs
  provide_mask, require_mask, lengths_mask, max_weight, match_weight = (
      _reduce_add(sources, extra))
  host.provide_mask |= provide_mask
  host.require_mask &= require_mask
  host.lengths_mask |= lengths_mask
  host.max_weight = max(host.max_weight, max_weight)
  host.match_weight = max(host.match_weight, match_weight)
  for source in sources:
    host.annotate(source.annotations())


def _merge_multiply(
    host: 'bloom_node.BloomNode',
    sources: List['bloom_node.BloomNode'],
    extra: list,
    **kwargs) -> None:
  del kwargs
  provide_mask, require_mask, lengths_mask, max_weight, match_weight = (
      _reduce_multiply(sources, extra))
  host.provide_mask &= provide_mask
  host.require_mask &= require_mask
  host.lengths_mask |= lengths_mask
  host.max_weight = max(host.max_weight, max_weight)
  host.match_weight = max(host.match_weight, match_weight)
  for source in sources:
    host.annotate(source.annotations())


def _merge_call(
    host: 'bloom_node.BloomNode',
    sources: List['bloom_node.BloomNode'],
    extra: list,
    **kwargs) -> None:
  assert len(extra) == 2
  call_args, call_kwargs = extra
  call_kwargs = call_kwargs.copy()
  call_fn = call_kwargs.pop('merge', None)
  if not call_fn:
    return
  call_kwargs.pop('visit', None)
  call_kwargs.update(kwargs)
  call_fn(host, sources, *call_args, **call_kwargs)


def _visit_identity(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> 'bloom_node.BloomNode':
  if not extra and len(sources) == 1:
    return sources[0]
  raise NotImplementedError(
      'OP_IDENTITY failed to reduce %s, %s' % (sources, extra))


def _reduce_add(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> Tuple[int, int, int, float, float]:
  if extra:
    raise NotImplementedError('OP_ADD failed to reduce %s' % extra)
  # Round up all of the values from all available sources.
  provide_mask = sources[0].provide_mask
  require_mask = sources[0].require_mask
  lengths_mask = sources[0].lengths_mask
  max_weight = sources[0].max_weight
  match_weight = sources[0].match_weight
  pos = 1
  l = len(sources)
  while pos < l:
    source = sources[pos]
    provide_mask |= source.provide_mask  # Letters from either are provided.
    require_mask &= source.require_mask  # Requirements are reduced.
    lengths_mask |= source.lengths_mask  # Lengths from either are provided.
    if source.max_weight > max_weight:
      max_weight = source.max_weight
    if source.match_weight > match_weight:
      match_weight = source.match_weight
    pos += 1
  return provide_mask, require_mask, lengths_mask, max_weight, match_weight


def _visit_add(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> Optional['bloom_node.BloomNode']:
  if len(sources) == 1:
    assert not extra
    return sources[0]
  provide_mask, require_mask, lengths_mask, max_weight, match_weight = (
    _reduce_add(sources, extra))
  reduced = bloom_node.BloomNode(_op_mixin.Op(_op_mixin.OP_ADD, sources))
  reduced.provide_mask = provide_mask
  reduced.require_mask = require_mask
  reduced.lengths_mask = lengths_mask
  reduced.max_weight = max_weight
  reduced.match_weight = match_weight
  return reduced


def _reduce_multiply(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> Tuple[int, int, int, float, float]:
  scale = 1
  for n in extra:
    scale *= n
  # First, verify there are matching masks. It's required for a valid
  # solution and is trivial to verify satisfaction.
  lengths_mask = sources[0].lengths_mask
  provide_mask = sources[0].provide_mask
  require_mask = sources[0].require_mask
  max_weight = sources[0].max_weight * scale
  match_weight = sources[0].match_weight * scale
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
  return provide_mask, require_mask, lengths_mask, max_weight, match_weight


def _visit_multiply(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> Optional['bloom_node.BloomNode']:
  if not extra and len(sources) == 1:
    return sources[0]
  provide_mask, require_mask, lengths_mask, max_weight, match_weight = (
      _reduce_multiply(sources, extra))
  if not any(source.op for source in sources) and (
      not lengths_mask or
      not max_weight or
      (require_mask and (provide_mask & require_mask) != require_mask)):
    # Unsatisfiable: no common requirements or child operations which could
    # potentially expand into more edges.
    return None
  # Verify all combinations are mutually satisfiable.
  for a, b in itertools.combinations(sources, 2):
    if not a.satisfies(b) or not b.satisfies(a):
      return None
  if extra:
    reduced = bloom_node.BloomNode(
        _op_mixin.Op(_op_mixin.OP_MULTIPLY, sources + extra))
  else:
    reduced = bloom_node.BloomNode(_op_mixin.Op(_op_mixin.OP_MULTIPLY, sources))
  reduced.provide_mask = provide_mask
  reduced.require_mask = require_mask
  reduced.lengths_mask = lengths_mask
  reduced.max_weight = max_weight
  reduced.match_weight = match_weight
  return reduced


def _visit_call(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> Optional['bloom_node.BloomNode']:
  assert len(extra) == 2
  call_args, call_kwargs = extra
  call_kwargs = call_kwargs.copy()
  call_kwargs.pop('merge', None)
  call_fn = call_kwargs.pop('visit', None)
  if not call_fn:
    return
  call_fn(sources, *call_args, **call_kwargs)



def _visit_fail(
    sources: List['bloom_node.BloomNode'],
    extra: list) -> None:
  del sources, extra
  raise NotImplementedError('Reduce visitor unsupported for this operator')


# Note: Order of operators must match _op_mixin.
_operator_functions = [
  (edge_mask_iter_util.iterable_common, iter_util.map_common, _merge_add, _visit_identity),
  (edge_mask_iter_util.iterable_both, iter_util.map_both, _merge_add, _visit_add),
  (edge_mask_iter_util.iterable_common, iter_util.map_common, _merge_multiply, _visit_multiply),
  (iter_util.map_none, iter_util.map_none, anagram_op.merge_fn, _visit_fail),
  (iter_util.map_none, iter_util.map_none, anagram_transform_op.merge_fn, _visit_fail),
  (edge_mask_iter_util.iterable_both, iter_util.map_both, _merge_call, _visit_call),
]
