import os
from typing import Any, Callable, Dict, IO, List, Type

_this_path = os.path.dirname(os.path.realpath(__file__))
_base_path = os.path.join(_this_path.split('/forge/')[0], 'forge')


T = Callable


def project_path(path: str) -> str:
  return os.path.join(_base_path, path)


def load(path: str, cls: Type[T]) -> Dict[str, T]:
  return load_lines(_read_lines(path), cls)


def load_lines(lines: List[str], cls: Type[T]) -> Dict[str, T]:
  acc = []
  last_group = None
  result = {}
  def maybe_flush_buffer() -> list:
    if acc and last_group:
      result[last_group] = cls(last_group, acc)
    return []
  for line in lines:
    line = line.rstrip('\n')
    if line.startswith('[') and line.endswith(']'):
      acc = maybe_flush_buffer()
      last_group = line.strip('[]')
    elif line:
      acc.append(line)
  maybe_flush_buffer()
  return result


def open_project_path(path: str, **kwargs: Any) -> IO:
  return open(project_path(path), **kwargs)


def _read_lines(path: str) -> List[str]:
  return open_project_path(path).readlines()
