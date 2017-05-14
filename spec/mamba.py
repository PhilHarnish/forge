from expects import *
from expects import matchers

# Mamba.
self = {}

def description(desc):
  del desc

def context(desc):
  del desc

def it(desc):
  del desc

class Hook(object):
  all = None
  each = None

before = Hook()
after = Hook()

# Expects.
if False:
  expect('no-op')  # Ensures import is not removed.

class be_between(matchers.Matcher):
  def __init__(self, low, high):
    self._low = low
    self._high = high

  def _match(self, subject):
    return subject > self._low and subject < self._high, []

  def _failure_message(self, subject, *args):
    return self._failure_message_negated(subject, *args).replace(' not ', ' ')

  def _failure_message_negated(self, subject, *args):
    return 'expected: %s not to be between %s and %s' % (
      subject, self._low, self._high)


class be_one_of(matchers.Matcher):
  def __init__(self, *args):
    self._options = args

  def _match(self, subject):
    return subject in self._options, [repr(option) for option in self._options]


# Sentinel object for undefined values.
_NOT_SET = {}

class call(object):
  def __init__(self, fn, *args, **kwargs):
    self._fn = fn
    self._args = args
    self._kwargs = kwargs
    self._cached_value = _NOT_SET

  @property
  def _value(self):
    if self._cached_value is _NOT_SET:
      self._cached_value = self._fn(*self._args, **self._kwargs)
    return self._cached_value

  def __repr__(self):
    args = ', '.join([
      repr(arg) for arg in self._args
    ] + [
      '%s=%s' % (key, repr(value)) for key, value in self._kwargs.items()
    ])
    if self._value is None:
      suffix = ''
    else:
      suffix = ' == %s' % repr(self._value)
    return '%s(%s)%s' % (self._fn.__name__, args, suffix)

  def __iter__(self):
    for v in self._value:
      yield v

  def __next__(self):
    return next(self._value)

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


class calling(call):
  """Returns an object which has yet-to-be called."""
  def __call__(self, *args, **kwargs):
    if args or kwargs:
      raise NotImplementedError()
    return self._value
