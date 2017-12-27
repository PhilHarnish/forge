from typing import Container, Iterable, List, Mapping, Optional, Tuple, TypeVar

T = TypeVar('T')  # Generic type.


def common(
    maps: List[Mapping[str, T]],
    whitelist: Optional[Container[str]] = None,
    blacklist: Optional[Container[str]] = None) -> Iterable[Tuple[str, List[T]]]:
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
    for key in reference if not any(key not in i for i in remaining)
  ]
