import textwrap

import mock
from expects import *
from expects import matchers

from spec.data import fixtures

fixtures.init()

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


class _have_been_called(matchers.Matcher):
  def __init__(self, *args, **kwargs):
    self._args = args
    self._kwargs = kwargs

  def __call__(self, *args, **kwargs):
    return _have_been_called(*args, **kwargs)

  def _match(self, subject):
    if self._args or self._kwargs:
      result = subject.call_args == mock.call(*self._args, **self._kwargs)
    else:
      result = subject.called
    return result, [str(c) for c in subject.call_args_list]

  def _failure_message(self, subject, *args):
    return self._failure_message_negated(subject, *args).replace(' not ', ' ')

  def _failure_message_negated(self, subject, *args):
    return 'expected: %s(%s) not to have been called' % (
      subject, _fmt_args(self._args, self._kwargs))


have_been_called = _have_been_called()
have_been_called_with = _have_been_called()


class have_been_called_times(matchers.Matcher):
  def __init__(self, times):
    self._times = times

  def __call__(self, times):
    return have_been_called_times(self._times)

  def _match(self, subject):
    return (self._times == len(subject.call_args_list),
        [str(c) for c in subject.call_args_list])

  def _failure_message(self, subject, *args):
    return self._failure_message_negated(subject, *args).replace(' not ', ' ')

  def _failure_message_negated(self, subject, *args):
    return 'expected: %s to have been called %s times' % (subject, self._times)


have_been_called_once = have_been_called_times(1)


# Sentinel object for undefined values.
_NOT_SET = {}

class call(object):
  def __init__(self, fn, *args, **kwargs):
    self._fn = fn
    self._args = args
    self._kwargs = kwargs
    self._cached_value = _NOT_SET
    self._cached_exception = None

  @property
  def _value(self):
    if self._cached_exception:
      raise self._cached_exception
    if self._cached_value is _NOT_SET:
      try:
        self._cached_value = self._fn(*self._args, **self._kwargs)
      except Exception as e:
        self._cached_exception = e
        raise e
    return self._cached_value

  def __repr__(self):
    args = _fmt_args(self._args, self._kwargs)
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


def _fmt_args(args, kwargs):
  return ', '.join([
                     repr(arg) for arg in args
                   ] + [
                     '%s=%s' % (key, repr(value)) for key, value in
                     kwargs.items()
                   ])


class look_like(equal):
  def __init__(self, expected):
    super(look_like, self).__init__(self._clean(expected))

  def _match(self, subject):
    cleaned = self._clean(subject)
    success, _ = super(look_like, self)._match(cleaned)
    return success, cleaned.split('\n')

  def _clean(self, s):
    return textwrap.dedent(s.rstrip(' ').strip('\n'))
