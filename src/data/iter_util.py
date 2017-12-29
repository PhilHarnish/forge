from typing import Container, Iterable, List, Mapping, Optional, Tuple, TypeVar

T = TypeVar('T')  # Generic type.


def both(
    maps: List[Mapping[str, T]],
    whitelist: Optional[Container[str]] = None,
    blacklist: Optional[Container[str]] = None
) -> Iterable[Tuple[str, List[T]]]:
  if not maps:
    return []
  if whitelist:
    reference = whitelist
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


def common(
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
    sorted_maps = list(sorted(maps, key=len, reverse=True))
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
