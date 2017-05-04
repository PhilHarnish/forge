from expects import *
from expects import matchers

# Mamba.
self = {}

def description(desc):
  pass

def context(desc):
  pass

def it(desc):
  pass

class Hook(object):
  all = None
  each = None

before = Hook()
after = Hook()

# Custom expects.
class call(object):
  def __init__(self, fn, *args, **kwargs):
    self._fn = fn
    self._args = args
    self._kwargs = kwargs
    value = fn(*args, **kwargs)
    self._value = value

  def __repr__(self):
    args = ', '.join([
      repr(arg) for arg in self._args
    ] + [
      '%s=%s' % (key, repr(value)) for key, value in self._kwargs.items()
    ])
    return '%s(%s)' % (self._fn.__name__, args)

  def __ge__(self, other):
    # NB: self._value.__gt__(other) will not work for [int] >= [float].
    return self._value >= other

  def __gt__(self, other):
    # NB: self._value.__gt__(other) will not work for [int] > [float].
    return self._value > other

  def __le__(self, other):
    # NB: self._value.__lt__(other) will not work for [int] <= [float].
    return self._value <= other

  def __lt__(self, other):
    # NB: self._value.__lt__(other) will not work for [int] < [float].
    return self._value < other

# Install simple overrides. This list could certainly be more exhaustive but
# there seem to be enough quirks with proxy objects it isn't obvious if a full
# list would be a good idea.
def _make_method(name):
  def method(self, *args, **kwargs):
    if hasattr(self._value, name):
      return getattr(self._value, name)(*args, **kwargs)
    return NotImplemented
  return method
for method in ['__eq__']:
  setattr(call, method, _make_method(method))
