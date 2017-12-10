from typing import Iterable, List, Tuple, TypeVar

T = TypeVar('T')  # Generic type.

def common(*iterables: List[T]) -> Iterable[Tuple[str, List[T]]]:
  if not iterables:
    return []
  sorted_iterables = list(sorted(iterables, key=len, reverse=True))
  result = []
  first, remaining = sorted_iterables[0], sorted_iterables[1:]
  for k in first:
    if any(k not in i for i in remaining):
      continue
    result.append((k, [i[k] for i in iterables]))
  return result
