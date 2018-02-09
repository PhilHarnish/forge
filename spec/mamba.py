import builtins
import random
import re
import textwrap
import time
from typing import Any, Iterable, Match, Optional

import mock
from expects import *
from expects import matchers

from data.convert import repr_format
from spec.data import fixtures

# Convenience.
fixtures.init()

def _init_breakpoint_global():
  setattr(builtins, 'breakpoint', lambda: None)


class _Breakpoints(object):
  """Allows for conditional breakpointing.

  Usage (in tests):
    with breakpoints:
      some_code()

  Usage (in code):
    breakpoint()  # Executes breakpoint() iff inside of with `breakpoints`.
  """
  def __enter__(self):
    def breakpoint():
      """Set breakpoint on this line."""
      print('Breakpoint here.')
    setattr(builtins, 'breakpoint', breakpoint)

  def __exit__(self, exc_type, exc_val, exc_tb):
    _init_breakpoint_global()

breakpoints = _Breakpoints()
_init_breakpoint_global()


TARGET_BENCHMARK_RUNTIME_MS = 500


class _Benchmark(object):
  def __init__(self, expected_ms, stddev) -> None:
    self._expected_ms = expected_ms
    self._stddev = stddev
    self._should_run = False

  def __enter__(self) -> bool:
    self._start = time.time()
    if self._expected_ms > TARGET_BENCHMARK_RUNTIME_MS:
      # Return True randomly such that the average time matches target.
      self._should_run = (
          random.random() < TARGET_BENCHMARK_RUNTIME_MS / self._expected_ms)
    else:
      self._should_run = True
    return self._should_run

  def __exit__(self, exc_type, exc_val, exc_tb) -> None:
    delta = (time.time() - self._start) * 1000
    if exc_type or exc_val or exc_tb:
      pass
    elif self._should_run:
      expect(delta).to(be_between(
          self._expected_ms * (1 - self._stddev),
          self._expected_ms * (1 + self._stddev)))
    elif delta > TARGET_BENCHMARK_RUNTIME_MS:
      raise Exception(
          'Benchmark of %s exceeds target of %s and should run infrequently' % (
            delta, TARGET_BENCHMARK_RUNTIME_MS,
          ))

  def __call__(
      self,
      expected_ms: Optional[int] = None,
      stddev: Optional[float] = .1) -> '_Benchmark':
    return _Benchmark(expected_ms, stddev)


benchmark = _Benchmark(5, 1)


# Mamba.
self = {}

def description(desc, tag=''):
  del desc
  del tag

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


def _fn_name(fn):
  if isinstance(fn, mock.MagicMock):
    return re.sub(r'^<.*name=\'([^\']*)\'.*$', r'\1', str(fn))
  elif hasattr(fn, '__name__'):
    return fn.__name__
  return str(fn)


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
      _fn_name(subject), repr_format.as_args(*self._args, **self._kwargs))


have_been_called = _have_been_called()
have_been_called_with = _have_been_called()


class have_been_called_times(matchers.Matcher):
  def __init__(self, times):
    self._times = times
    self._actual_times = 'unknown'

  def __call__(self, times):
    return have_been_called_times(self._times)

  def _match(self, subject):
    self._actual_times = len(subject.call_args_list)
    return (self._times == self._actual_times,
        [str(c) for c in subject.call_args_list])

  def _failure_message(self, subject, *args):
    return self._failure_message_negated(subject, *args).replace(' not ', ' ')

  def _failure_message_negated(self, subject, *args):
    return (
      'expected: %s to have been called %s times,'
      ' called %s times instead' % (
        _fn_name(subject), self._times, self._actual_times
      )
    )


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
    args = repr_format.as_args(*self._args, **self._kwargs)
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


class look_like(equal):
  def __init__(self, expected, remove_comments=False):
    self._remove_comments = remove_comments
    super(look_like, self).__init__(self._clean(expected))

  def _match(self, subject):
    cleaned = self._clean(subject)
    success, _ = super(look_like, self)._match(cleaned)
    error_lines = ['looks like:'] + textwrap.indent(cleaned, ' ').split('\n')
    return success, error_lines

  def _clean(self, s):
    if self._remove_comments:
      def sub(m: Match[str]) -> str:
        if m.group(2) is None:
          return m.group(1)
        return ''

      pattern = r'(\".*?\"|\'.*?\')|(\s*#[^\r\n]*$)'
      s = re.compile(pattern, re.MULTILINE | re.DOTALL).sub(sub, s)

    return textwrap.dedent(s.rstrip(' ').strip('\n'))


def path_values(root: Any, path: Iterable) -> str:
  results = [repr(root)]
  cursor = root
  for c in path:
    cursor = cursor[c]
    results.append('%s = %s' % (c, repr(cursor)))
  return '\n'.join(results)
