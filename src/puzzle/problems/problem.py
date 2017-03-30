_PROBLEM_TYPES = set()

class Problem(object):
  def __init__(self, src):
    self.src = src

def register(cls):
  _PROBLEM_TYPES.add(cls)

def problem_types():
  return _PROBLEM_TYPES

def unregister_all():
  _PROBLEM_TYPES.clear()
