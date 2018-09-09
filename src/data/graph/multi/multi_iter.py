import collections
from typing import Dict, Iterable, List, Tuple

from data import max_heap, types
from data.graph.multi import multi_state

ResultIn = Tuple[multi_state.State, types.WeightedWord]
ResultOut = Tuple[multi_state.State, Tuple[types.WeightedWord]]
_EXHAUSTED = {}


def multi_iter(sources: Iterable[Iterable[ResultIn]]) -> Iterable[ResultOut]:
  iterators = [iter(source) for source in sources]
  bucket_groups = [collections.defaultdict(list) for _ in sources]
  bucket_weights = [None for _ in sources]
  max_bucket_weights = [0 for _ in sources]
  hole_bucket_weights = []
  single_group = {}  # Reusable entry when mutating a specific bucket group.
  single_list = [None]
  result_heap = max_heap.MaxHeap()
  # Prime mutation_heap.
  mutation_heap = max_heap.MaxHeap()
  max_weight = float('inf')  # TODO: Prime state before starting iteration.
  for pos, iterator in enumerate(iterators):
    value = next(iterator, _EXHAUSTED)
    if value is _EXHAUSTED:
      return
    _, (_, weight) = value
    mutation_heap.push(weight, (pos, value))
  while mutation_heap:
    pos, (state, weighted_word) = mutation_heap.pop()
    single_group.clear()
    single_list[0] = weighted_word
    single_group[state] = single_list
    swap, bucket_groups[pos] = bucket_groups[pos], single_group
    for weight, result in _emit(bucket_groups):
      result_heap.push(weight, result)
    if result_heap:
      _, weight = weighted_word
      max_weight = _max_weight(
          max_bucket_weights, hole_bucket_weights, pos, weight)
    while result_heap and result_heap.best_weight() > max_weight:
      heap_pop = result_heap.pop()
      yield heap_pop
    single_group, bucket_groups[pos] = bucket_groups[pos], swap
    _, mutation_weight = weighted_word
    if bucket_weights[pos]:  # Attempt to merge.
      bucket_weight = bucket_weights[pos]
      if bucket_weight != mutation_weight:
        bucket_groups[pos].clear()
        bucket_weights[pos] = mutation_weight
    else:
      max_bucket_weights[pos] = mutation_weight
    bucket_groups[pos][state].append(weighted_word)
    # Prepare next mutation.
    next_value = next(iterators[pos], _EXHAUSTED)
    if next_value is not _EXHAUSTED:
      _, (_, next_weight) = next_value
      mutation_heap.push(next_weight, (pos, next_value))
  while result_heap:
    yield result_heap.pop()


def _max_weight(
    max_bucket_weights: List[float], hole_bucket_weights: List[float], pos: int,
    weight: float) -> float:
  # TODO: This can be precomputed.
  if not hole_bucket_weights:
    if any(weight == 0 for weight in max_bucket_weights):
      return weight
    for x in range(len(max_bucket_weights)):
      acc = 1
      for i, value in enumerate(max_bucket_weights):
        if i == x:
          continue
        acc *= value
      hole_bucket_weights.append(acc)
  return hole_bucket_weights[pos] * weight


def _emit(
    bucket_groups: List[Dict[multi_state.State, types.WeightedWord]]
) -> Iterable[Tuple[float, ResultOut]]:
  result = [None for _ in bucket_groups]
  end = len(bucket_groups) - 1
  def recurse(
      state_acc: multi_state.State, weight_acc: float, pos: int) -> None:
    for state, values in bucket_groups[pos].items():
      state_next = state_acc & state
      if state_next is None:
        continue
      for value in values:
        result[pos] = value
        _, weight = value
        weight_next = weight_acc * weight
        if pos == end:
          yield weight_next, (state_next, tuple(result))
        else:
          yield from recurse(state_next, weight_next, pos + 1)
  yield from recurse(multi_state.BLANK, 1, 0)
