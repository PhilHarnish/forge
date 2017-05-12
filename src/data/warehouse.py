_DATA = {}

def register(path, value):
  if path in _DATA:
    raise KeyError('%s already specified' % path)
  _DATA[path] = value

def get(path):
  value = _DATA[path]
  if callable(value):
    _DATA[path] = value()
  return _DATA[path]

def init():
  if _DATA:
    raise Exception('Already initialized')
  _DATA['initialized'] = True

def reset():
  _DATA.clear()
