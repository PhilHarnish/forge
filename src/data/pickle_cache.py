import hashlib
import os
import pickle
import re

from data import data

_PICKLE_PATH = data.project_path('data/_pkl_cache')
_SANITIZE_RE = re.compile(r'[^A-Za-z1-9]')


def cache(prefix):
  def decorator(fn):
    def fn_wrapper(*args, **kwargs):
      pickle_src = _path_for_prefix_and_args(prefix, args, kwargs)
      parent_dir = os.path.dirname(pickle_src)
      if not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
      if os.path.exists(pickle_src):
        result = pickle.load(_open_pkl_path(pickle_src, 'rb'))
      else:
        result = fn(*args, **kwargs)
        pickle.dump(result, _open_pkl_path(pickle_src, 'wb'))
      return result

    return fn_wrapper

  return decorator


def _open_pkl_path(path, mode):
  return open(path, mode)


def _path_for_prefix_and_args(prefix, args, kwargs):
  parts = [_PICKLE_PATH, prefix]
  if not args and not kwargs:
    parts.append('_')
  if args:
    parts.append(_sanitize_list(args))
  if kwargs:
    parts.append(_sanitize_dict(kwargs))
  return os.path.join(*parts) + '.pkl'


def _sanitize(o):
  if isinstance(o, dict):
    return _sanitize_dict(o)
  elif isinstance(o, list):
    return _sanitize_list(o)
  elif o == '':
    return '_empty_str'
  as_str = repr(o)
  sanitized = _SANITIZE_RE.sub('', as_str)
  if sanitized:
    return sanitized
  # No information preserved after sanitizing.
  return '_' + _hash(as_str)


def _sanitize_list(o):
  if not o:
    return '_empty_list'
  return ','.join(_sanitize(i) for i in o)


def _sanitize_dict(o):
  if not o:
    return '_empty_dict'
  sorted_items = sorted(o.items(), key=lambda i: i[0])
  return ','.join(
      '%s-%s' % (_sanitize(k), _sanitize(v)) for k, v in sorted_items
  )


def _hash(s):
  return hashlib.md5(bytes(s, encoding='UTF-8')).hexdigest()[:9]
