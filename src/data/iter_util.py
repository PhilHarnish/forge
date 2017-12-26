from typing import Container, Iterable, List, Mapping, Optional, Tuple, TypeVar

T = TypeVar('T')  # Generic type.


def common(
    maps: List[Mapping[str, T]],
    skip: Optional[Container[str]] = None) -> Iterable[Tuple[str, List[T]]]:
  if not maps:
    return []
  sorted_maps = list(sorted(maps, key=len, reverse=True))
  first, remaining = sorted_maps[0], sorted_maps[1:]
  if skip:
    return [
      (key, [i[key] for i in maps])
      for key in first if key not in skip and not any(
          key not in i for i in remaining)
    ]
  return [
    (key, [i[key] for i in maps])
    for key in first if not any(key not in i for i in remaining)
  ]
