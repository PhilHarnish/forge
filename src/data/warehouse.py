import collections
import time

_DATA = {}
_HISTORY = []
_DEADLINE_MS = 10


def register(path, value):
  if path in _DATA:
    raise KeyError('%s already specified' % path)
  _DATA[path] = value


def get(path):
  value = _DATA[path]
  if callable(value):
    start = time.time()
    _DATA[path] = value()
    delta = (time.time() - start) * 1000
    if delta > _DATA['_DEADLINE_MS']:
      raise Exception('Deadline exceeded loading %s (%.0f ms)' % (path, delta))
  return _DATA[path]


def init(register_base=True):
  if _DATA:
    raise Exception('Already initialized')
  _DATA['_INITIALIZED'] = True
  _DATA['_DEADLINE_MS'] = _DEADLINE_MS
  if register_base:
    register('/letter/frequency', _get_letter_frequency)


def reset():
  _DATA.clear()


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
