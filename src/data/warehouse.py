import collections
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


def init(register_base=True):
  if _DATA:
    raise Exception('Already initialized')
  _DATA['initialized'] = True
  if register_base:
    register('/letter/frequency', _get_letter_frequency)

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


def _get_letter_frequency():
  return collections.OrderedDict(sorted(list(zip('abcdefghijklmnopqrstuvwxyz', [
    # abcdef.
    9081174698, 419765694, 596623239, 361493758, 593086170, 297285731,
    # ghijkl.
    227771642, 220523502, 3086225277, 180739802, 195647953, 252900442,
    341583838, 437961375, 246429812, 303249898, 139563801, 323534251,  # mnopqr.
    565123981, 388448018, 179615587, 204486977, 252231566, 508609523,  # stuvwx.
    195011703, 132095202,  # yz.
  ])), key=lambda x: x[1], reverse=True))
