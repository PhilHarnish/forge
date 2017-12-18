from typing import Iterable, List, Mapping, Tuple, TypeVar

T = TypeVar('T')  # Generic type.

def common(maps: List[Mapping[str, T]]) -> Iterable[Tuple[str, List[T]]]:
  if not maps:
    return []
  sorted_maps = list(sorted(maps, key=len, reverse=True))
  result = []
  first, remaining = sorted_maps[0], sorted_maps[1:]
  for key in first:
    if any(key not in i for i in remaining):
      continue
    result.append((key, [i[key] for i in maps]))
  return result
