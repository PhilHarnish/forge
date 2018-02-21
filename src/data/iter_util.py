from typing import Callable, Container, Iterable, List, Mapping, Optional, \
  Tuple, TypeVar

T = TypeVar('T')  # Generic type.


def map_both(
    maps: List[Mapping[str, T]],
    whitelist: Optional[Iterable[str]] = None,
    blacklist: Optional[Container[str]] = None,
) -> Iterable[Tuple[str, List[T]]]:
  if not maps:
    return []
  if whitelist:
    reference = {key for key in whitelist if any(key in map for map in maps)}
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
