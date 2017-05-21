import os
import pickle

from data import data

_DATA = {}
_HISTORY = []
_PICKLE = set()
_PICKLE_PATH = data.project_path('data/')


def register(path, value, pickle=False):
  if path in _DATA:
    raise KeyError('%s already specified' % path)
  _DATA[path] = value
  if pickle:
    _PICKLE.add(path)

def get(path):
  value = _DATA[path]
  if callable(value):
    if path in _PICKLE:
      pickle_src = os.path.join(_PICKLE_PATH, path.replace('/', '_') + '.pkl')
      if os.path.exists(pickle_src):
        # Read from pkl.
        _DATA[path] = pickle.load(_open_pkl_path(pickle_src, 'rb'))
      else:
        # Save to pkl.
        _DATA[path] = value()
        try:
          pickle.dump(_DATA[path], _open_pkl_path(pickle_src, 'wb'))
        except Exception as e:
          print(e)
          raise e
    else:
      _DATA[path] = value()
  return _DATA[path]


def _open_pkl_path(path, mode):
  return open(path, mode)

def init():
  if _DATA:
    raise Exception('Already initialized')
  _DATA['initialized'] = True

def reset():
  _DATA.clear()
  _PICKLE.clear()


def save():
  global _DATA
  _HISTORY.append(_DATA)
  _DATA = {}


def restore():
  global _DATA
  _DATA = _HISTORY.pop()
