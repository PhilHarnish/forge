from typing import Callable, Container, Iterable, List, Mapping, Optional, \
  Tuple, TypeVar

T = TypeVar('T')  # Generic type.
_EXHAUSTED = {}


def map_both(
    maps: List[Mapping[str, T]],
    whitelist: Optional[Iterable[str]] = None,
    blacklist: Optional[Container[str]] = None,
) -> Iterable[Tuple[str, List[T]]]:
  if not maps:
    return []
  if whitelist:
    reference = {key for key in whitelist if any(key in m for m in maps)}
  else:
    # Combine keys from all maps as reference.
    reference = set()
    for m in maps:
      reference.update(m.keys())
  if blacklist:
    return [
      (key, [i[key] for i in maps if key in i])
      for key in reference if key not in blacklist
    ]
  return [
    (key, [i[key] for i in maps if key in i])
    for key in reference
  ]


def map_common(
    maps: List[Mapping[str, T]],
    whitelist: Optional[Container[str]] = None,
    blacklist: Optional[Container[str]] = None
) -> Iterable[Tuple[str, List[T]]]:
  if not maps:
    return []
  if whitelist:
    reference = whitelist
    remaining = maps
  else:
    # Use smallest input map as reference.
    sorted_maps = list(sorted(maps, key=len))
    reference, remaining = sorted_maps[0], sorted_maps[1:]
  if blacklist:
    return [
      (key, [i[key] for i in maps])
      for key in reference if key not in blacklist and not any(
          key not in i for i in remaining)
    ]
  return [
    (key, [i[key] for i in maps])
    for key in reference if all(key in i for i in remaining)
  ]


def map_none(
    maps: List[Mapping[str, T]],
    whitelist: Optional[Iterable[str]] = None,
    blacklist: Optional[Container[str]] = None
) -> Iterable[Tuple[str, List[T]]]:
  del maps, whitelist, blacklist
  return []


def reduce_binary(
    func: Callable[[T, T], T],
    items: Iterable[T],
    initializer: Optional[T] = None) -> T:
  """Call `func` with pairs of items until exhausted.

   Execution order is undefined.
   """
  items = list(items)
  if initializer:
    items.append(initializer)
  while len(items) > 1:
    queue = []
    while len(items) >= 2:
      queue.append(func(items.pop(), items.pop()))
    if items:
      queue.append(items.pop())
    items = queue
  return items[0]


def ensure_prefix(
    source: Iterable[str], reference: Iterable[str],
    delimiter: str = ' ') -> Iterable[str]:
  """Returns iterable which ensures `source` always prefix `reference`."""
  source_iter = iter(source)
  source_next = next(source_iter, _EXHAUSTED)
  last_yield = None
  for ref in reference:
    while source_next is not _EXHAUSTED:
      expected_delimiter_pos = len(source_next)
      if (len(ref) > expected_delimiter_pos and
          ref[expected_delimiter_pos] == delimiter and
          ref.startswith(source_next)):
        pass  # NB: source_next == ref_left yields below.
      elif source_next < ref:
        yield source_next
      else:
        break
      source_next = next(source_iter, _EXHAUSTED)
    ref_left, _, _ = ref.rstrip(delimiter).rpartition(delimiter)
    if last_yield != ref_left:
      yield ref_left
    last_yield = ref_left
  if source_next is not _EXHAUSTED:
    yield source_next
    yield from source_iter


def iter_alphabetical_prefixes(
    iterables: List[Iterable[str]],
    delimiter: str = ' ') -> Iterable[Tuple[str, Optional[tuple]]]:
  """Iter through all iterables simultaneously and yield grouped results.

  Yields once for each item in iterables[0] such that result[1:] is a prefix of
  result[0].
  """
  if not iterables:
    return
  cursors = [iter(i) for i in iterables]
  next_values = [next(c, _EXHAUSTED) for c in cursors]
  last_pos = len(iterables) - 1
  results = []
  stack = [('', results)]
  while True:
    if all(v is _EXHAUSTED for v in next_values):
      break
    pos = len(stack) - 1
    parent, children = stack[pos]
    next_value = next_values[pos]
    expected_delimiter_pos = len(parent)
    prefix_match = expected_delimiter_pos == 0 or (
        len(next_value) > expected_delimiter_pos and
        next_value[expected_delimiter_pos] == delimiter and
        next_value.startswith(parent))
    if next_value is not _EXHAUSTED and prefix_match:
      pass  # Go deeper.
    elif children is results:  # At end of stack.
      yield from results
      results.clear()
    else:
      stack.pop()  # Return up stack and retry.
      continue
    next_values[pos] = next(cursors[pos], _EXHAUSTED)
    if pos < last_pos:
      stack.append((next_value, []))
      children.append(stack[pos + 1])
    else:
      # At the end of iterables.
      children.append((next_value, None))
  yield from results
