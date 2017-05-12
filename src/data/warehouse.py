_DATA = {}

def register(path, value):
  _DATA[path] = value

def get(path):
  return _DATA[path]

def reset():
  _DATA.clear()
