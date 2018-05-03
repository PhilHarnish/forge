import functools
import hashlib
import os
import pickle
import re
import sys
from typing import Any, Callable, IO, Iterable

from data import data

_PICKLE_PATH = data.project_path('data/_pkl_cache')
_SANITIZE_RE = re.compile(r'[^A-Za-z0-9]')
_DEFAULT_CACHE_SIZE = 16
_DISABLED_PREFIXES = {}


TransformFn = Callable[[Callable], Callable]
TestFn = Callable[[str, tuple, dict], bool]


def cache(prefix: str) -> TransformFn:
  def test_fn(pickle_source: str, args: tuple, kwargs: dict) -> bool:
    del args, kwargs
    # Always use pickle_source if present.
    return os.path.exists(pickle_source)
  return _cache(prefix, test_fn)


def cache_from_file(
    prefix: str, path_fn: Callable = lambda *args: args[-1]) -> TransformFn:
  def test_fn(pickle_source: str, args: tuple, kwargs: dict) -> bool:
    file_source = path_fn(*args, **kwargs)
    if 'pickle_cache_spec' in file_source:
      return False  # Quick fix to make testing easy.
    resolved_file = _resolve_path(file_source)
    if not os.path.exists(pickle_source):
      return False
    return os.path.getmtime(pickle_source) > os.path.getmtime(resolved_file)
  return _cache(prefix, test_fn)


def disable(prefixes: Iterable) -> None:
  for prefix in prefixes:
    _DISABLED_PREFIXES[prefix] = 0


def enable(prefixes: Iterable) -> None:
  for prefix in prefixes:
    del _DISABLED_PREFIXES[prefix]


def _cache(prefix: str, test_fn: TestFn) -> TransformFn:
  def decorator(fn: Callable) -> Callable:
    @functools.lru_cache(
        maxsize=_DISABLED_PREFIXES.get(prefix, _DEFAULT_CACHE_SIZE))
    def fn_wrapper(*args: Any, **kwargs: Any) -> Any:
      if prefix in _DISABLED_PREFIXES:
        return fn(*args, **kwargs)
      pickle_src = _path_for_prefix_and_args(prefix, args, kwargs)
      # TODO: Benchmark zip read performance.
      parent_dir = os.path.dirname(pickle_src)
      if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
      if test_fn(pickle_src, args, kwargs):
        result = pickle.load(_open_pkl_path(pickle_src, 'rb'))
      else:
        result = fn(*args, **kwargs)
        # TODO: Add async support.
        pickle.dump(
            result,
            _open_pkl_path(pickle_src, 'wb'),
            protocol=pickle.HIGHEST_PROTOCOL)
      return result

    return fn_wrapper

  return decorator


def _resolve_path(file_source: str) -> str:
  for base in sys.path:
    candidate = os.path.join(base, file_source)
    if os.path.exists(candidate):
      return candidate
  raise IOError('Unable to stat %s' % file_source)


def _open_pkl_path(path: str, mode: str) -> IO:
  return open(path, mode)


def _path_for_prefix_and_args(prefix: str, args: tuple, kwargs: dict):
  parts = [_PICKLE_PATH, prefix]
  if not args and not kwargs:
    parts.append('_')
  if args:
    parts.append(_sanitize_list(args))
  if kwargs:
    parts.append(_sanitize_dict(kwargs))
  return os.path.join(*parts) + '.pkl'


def _sanitize(o: Any) -> str:
  if isinstance(o, dict):
    return _sanitize_dict(o)
  elif isinstance(o, list):
    return _sanitize_list(o)
  elif o == '':
    return '_empty_str'
  as_str = repr(o)
  if as_str.startswith('<') and as_str.endswith('>'):
    as_str = as_str.strip('<>').split(' object at ')[0]
  sanitized = _SANITIZE_RE.sub('', as_str)
  if sanitized:
    return sanitized
  # No information preserved after sanitizing.
  return '_' + _hash(as_str)


def _sanitize_list(o: Iterable) -> str:
  if not o:
    return '_empty_list'
  return ','.join(_sanitize(i) for i in o)


def _sanitize_dict(o: dict) -> str:
  if not o:
    return '_empty_dict'
  sorted_items = sorted(o.items(), key=lambda i: i[0])
  return ','.join(
      '%s-%s' % (_sanitize(k), _sanitize(v)) for k, v in sorted_items
  )


def _hash(s: str) -> str:
  return hashlib.md5(bytes(s, encoding='UTF-8')).hexdigest()[:9]
