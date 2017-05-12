_DATA = {}

def register(path, value):
  _DATA[path] = value

def get(path):
  return _DATA[path]

def init():
  if _DATA:
    raise Exception('Already initialized')
  _DATA['initialized'] = True

def reset():
  _DATA.clear()
