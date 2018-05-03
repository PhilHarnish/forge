import functools
import gzip
import hashlib
import os
import pickle
import re
import sys
from typing import Any, Callable, IO, Iterable

from data import data
from util import perf

_PICKLE_PATH = data.project_path('data/_pkl_cache')
_SANITIZE_RE = re.compile(r'[^A-Za-z0-9]')
_DEFAULT_CACHE_SIZE = 16
_DISABLED_PREFIXES = {}


read = perf.Perf('read', ['pkl', 'pkl.gz'])
"""
read
pkl: 192.12/s, 1.37x (114 calls, 593.38u)
pkl.gz: 140.05/s, 1.00x (114 calls, 813.99u)
"""
write = perf.Perf('write', ['pkl', 'pkl.gz'])
"""
write
pkl: 261.02/s, 18.07x (116 calls, 444.41u)
pkl.gz: 14.45/s, 1.00x (116 calls, 8028.63u)
"""


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
      pickle_source = _path_for_prefix_and_args(prefix, args, kwargs)
      parent_dir = os.path.dirname(pickle_source)
      if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
      if test_fn(pickle_source, args, kwargs):
        result = _pickle_load(pickle_source)
      else:
        result = fn(*args, **kwargs)
        _pickle_dump(pickle_source, result)
      return result

    return fn_wrapper

  return decorator


def _pickle_load(pickle_source: str) -> Any:
  pickle_gzip_source = '%s.gz' % pickle_source
  if os.path.exists(pickle_gzip_source):
    with read.benchmark('pkl.gz'):
      f = _open_gzip(pickle_gzip_source, 'rb')
      pickle.load(f)

  with read.benchmark('pkl'):
    f = _open_path(pickle_source, 'rb')
    pkl = pickle.load(f)
  return pkl


def _pickle_dump(pickle_source: str, data: Any) -> None:
  # TODO: Add async support.
  with write.benchmark('pkl'):
    pickle.dump(
        data,
        _open_path(pickle_source, 'wb'),
        protocol=pickle.HIGHEST_PROTOCOL)
  with write.benchmark('pkl.gz'):
    pickle_gzip_source = '%s.gz' % pickle_source
    pickle.dump(
        data,
        _open_gzip(pickle_gzip_source, 'wb'),
        protocol=pickle.HIGHEST_PROTOCOL)


def _resolve_path(file_source: str) -> str:
  for base in sys.path:
    candidate = os.path.join(base, file_source)
    if os.path.exists(candidate):
      return candidate
  raise IOError('Unable to stat %s' % file_source)


def _open_path(path: str, mode: str) -> IO:
  return open(path, mode)


def _open_gzip(path: str, mode: str) -> IO:
  return gzip.open(path, mode=mode)


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
