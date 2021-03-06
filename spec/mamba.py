import builtins
import contextlib
import math
import random
import re
import textwrap
import time
from typing import *
from typing import Match

import mock
from expects import *
from expects import matchers
from mamba import example, formatters, runnable

from data.convert import repr_format
from spec.data import fixtures
# Convenience.
from util import perf

fixtures.init()


class CustomFormatter(formatters.ProgressFormatter):
  def __init__(self, settings) -> None:
    super(CustomFormatter, self).__init__(settings)
    formatters.sys.stdout.isatty = lambda: not settings.no_color
    self.slow_examples = []

  def append_slow_example(self, ex: example.Example, note: str) -> None:
    self.slow_examples.append(
        '%s is slow%s' % (self._format_full_example_name(ex), note))

  def summary(
      self, duration, example_count, failed_count, pending_count) -> None:
    if self.slow_examples:
      formatters.puts()
      formatters.puts('\n'.join(self.slow_examples))
    formatters.puts(perf.report())
    super(CustomFormatter, self).summary(
        duration, example_count, failed_count, pending_count)

  def example_passed(self, ex: example.Example):
    super(CustomFormatter, self).example_passed(ex)
    slow_note = self._format_slow_test(ex)
    if slow_note:
      self.append_slow_example(ex, slow_note)

  def example_failed(self, ex: example.Example):
    super(CustomFormatter, self).example_failed(ex)
    slow_note = self._format_slow_test(ex)
    if slow_note:
      self.append_slow_example(ex, slow_note)

  def _format_traceback(self, ex: example.Example) -> str:
    tb = self._traceback(ex)
    messages = []
    strip = False  # Do not strip when libraries are at top of error.
    for message in reversed(formatters.traceback.format_tb(tb)):
      if strip and '/expects/' in message or '/spec/mamba.py' in message:
        continue  # Skip intermediate libraries in middle of stack.
      else:
        strip = True
        messages.append(message[2:])
    return ''.join(messages)


def traceback() -> None:
  import traceback
  for line in traceback.format_stack()[:-1]:
    print(line.strip())


def _init_globals() -> None:
  setattr(builtins, 'breakpoint', lambda: None)
  setattr(builtins, 'traceback', traceback)


class _Breakpoints(object):
  """Allows for conditional breakpointing.

  Usage (in tests):
    with breakpoints:
      some_code()

  Usage (in code):
    breakpoint()  # Executes breakpoint() iff inside of with `breakpoints`.
  """
  def __enter__(self) -> None:
    def breakpoint() -> None:
      """Set breakpoint on this line."""
      print('Breakpoint here.')
    setattr(builtins, 'breakpoint', breakpoint)

  def __exit__(self, exc_type, exc_val, exc_tb) -> None:
    _init_globals()

breakpoints = _Breakpoints()
_init_globals()


TARGET_BENCHMARK_RUNTIME_MS = 500


class _Benchmark(object):
  def __init__(self, expected_ms: int, stddev: float) -> None:
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
    if not self._should_run:
      raise runnable.SkipException('Skipping with probability %s / %s' % (
          TARGET_BENCHMARK_RUNTIME_MS, self._expected_ms))
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

_CollectorContext = Generator[Any, Any, None]

@contextlib.contextmanager
def gather_exceptions() -> Generator[Callable[[], _CollectorContext], Any, Any]:
  exceptions = []
  @contextlib.contextmanager
  def collector() -> _CollectorContext:
    try:
      yield
    except Exception as e:
      exceptions.append(e)
  collector.exceptions = exceptions
  def has_no_exceptions() -> None:
    if not exceptions:
      return
    if len(exceptions) > 1:
      plural = 's'
    else:
      plural = ''
    result = ['%s exception%s caught:' % (len(exceptions), plural)]
    for i, exception in enumerate(exceptions):
      result.append('#%(pos)s %(name)s raised with:\n%(body)s' % {
        'pos': i + 1,
        'name': type(exception).__name__,
        'body': textwrap.indent(str(exception.args[0]).strip(), '   '),
      })
    exceptions.clear()  # Allows unit tests to consume and assert exceptions.
    raise AssertionError('\n'.join(result))
  collector.has_no_exceptions = has_no_exceptions
  try:
    yield collector
  except Exception as e:
    exceptions.append(
        AssertionError('Exception raised outside of collector (see next).'
            ' Use `with collector()` to collect exceptions.'))
    exceptions.append(e)
  collector.has_no_exceptions()


# Mamba.
self = {}

def description(desc: str, tag: str = '') -> None:
  del desc
  del tag

def context(desc: str) -> None:
  del desc

def it(desc: str) -> None:
  del desc

class Hook(object):
  all = None
  each = None

before = Hook()
after = Hook()

# Expects.
expect('no-op')  # Ensures import is not removed.

class be_between(matchers.Matcher):
  def __init__(self, low: float, high: float) -> None:
    self._low = low
    self._high = high

  def _match(self, subject: Any) -> tuple:
    return self._low < subject < self._high, []

  def _failure_message(self, subject: Any, *args: Iterable[Any]) -> str:
    return self._failure_message_negated(subject, *args).replace(' not ', ' ')

  def _failure_message_negated(self, subject: Any, *args: Iterable[Any]) -> str:
    return 'expected: %s not to be between %s and %s' % (
      subject, self._low, self._high)


class be_close_to(matchers.Matcher):
  def __init__(
      self, other: float, relative_tolerance: Optional[float] = None,
      *args, **kwargs
  ) -> None:
    self._other = other
    self._args = args
    self._kwargs = kwargs
    if relative_tolerance is not None:
      self._kwargs['rel_tol'] = relative_tolerance

  def _match(self, subject: Any) -> tuple:
    min_value = min(subject, self._other)
    max_value = max(subject, self._other)
    required_tolerance = 1 - (min_value / max_value)
    return math.isclose(subject, self._other, *self._args, **self._kwargs), [
      '%s requires relative_tolerance=%s' % (
        str(self._other), required_tolerance)]


class be_one_of(matchers.Matcher):
  def __init__(self, *args: Any) -> None:
    self._options = args

  def _match(self, subject: Any) -> tuple:
    return subject in self._options, [repr(option) for option in self._options]


class _be_unique(matchers.Matcher):
  def _match(self, subject: Any) -> tuple:
    subject = list(subject)
    ids = set()
    hashes = set()
    for i in subject:
      i_id = id(i)
      if i_id in ids:
        return False, subject
      ids.add(i_id)
      try:
        i_hash = hash(i)
      except TypeError:
        i_hash = hash(repr(i))
      if i_hash in hashes:
        return False, subject
      hashes.add(i_hash)
    return True, []


be_unique = _be_unique()


def _fn_name(fn: Callable):
  if isinstance(fn, mock.MagicMock):
    return re.sub(r'^<.*name=\'([^\']*)\'.*$', r'\1', str(fn))
  elif hasattr(fn, '__name__'):
    return fn.__name__
  return str(fn)


class _have_been_called(matchers.Matcher):
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    self._args = args
    self._kwargs = kwargs

  def __call__(self, *args: Any, **kwargs: Any) -> matchers.Matcher:
    return _have_been_called(*args, **kwargs)

  def _match(self, subject: Any) -> tuple:
    if self._args or self._kwargs:
      result = subject.call_args == mock.call(*self._args, **self._kwargs)
    else:
      result = subject.called
    return result, [str(c) for c in subject.call_args_list]

  def _failure_message(self, subject, *args) -> str:
    return self._failure_message_negated(subject, *args).replace(' not ', ' ')

  def _failure_message_negated(self, subject, *args) -> str:
    return 'expected: %s(%s) not to have been called\nbut:\n%s' % (
      _fn_name(subject), repr_format.as_args(*self._args, **self._kwargs),
      '\n'.join('\n'.join(arg) for arg in args))


have_been_called = _have_been_called()
have_been_called_with = _have_been_called()


class have_been_called_times(matchers.Matcher):
  def __init__(self, times: int) -> None:
    self._times = times
    self._actual_times = 'unknown'

  def __call__(self, times: int) -> matchers.Matcher:
    return have_been_called_times(self._times)

  def _match(self, subject: Any) -> tuple:
    self._actual_times = len(subject.call_args_list)
    return (self._times == self._actual_times,
        [str(c) for c in subject.call_args_list])

  def _failure_message(self, subject: Any, *args: Any) -> str:
    return self._failure_message_negated(subject, *args).replace(' not ', ' ')

  def _failure_message_negated(self, subject: Any, *args: Any) -> str:
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
  def __init__(self, fn: Callable, *args: Any, **kwargs: Any) -> None:
    self._fn = fn
    self._args = args
    self._kwargs = kwargs
    self._cached_value = _NOT_SET
    self._cached_exception = None

  @property
  def _value(self) -> Any:
    if self._cached_exception:
      raise self._cached_exception
    if self._cached_value is _NOT_SET:
      try:
        self._cached_value = self._fn(*self._args, **self._kwargs)
      except Exception as e:
        self._cached_exception = e
        raise e
    return self._cached_value

  @property
  def __class__(self) -> Type:
    return type(self._value)

  def __repr__(self) -> str:
    args = repr_format.as_args(*self._args, **self._kwargs)
    if self._value is None:
      suffix = ''
    else:
      suffix = ' == %s' % repr(self._value)
    return '%s(%s)%s' % (self._fn.__name__, args, suffix)

  def __iter__(self) -> Iterable:
    for v in self._value:
      yield v

  def __next__(self) -> Any:
    return next(self._value)

  def __ge__(self, other: Any) -> bool:
    # NB: self._value.__gt__(other) will not work for [int] >= [float].
    return self._value >= other

  def __gt__(self, other: Any) -> bool:
    # NB: self._value.__gt__(other) will not work for [int] > [float].
    return self._value > other

  def __le__(self, other: Any) -> bool:
    # NB: self._value.__lt__(other) will not work for [int] <= [float].
    return self._value <= other

  def __lt__(self, other: Any) -> bool:
    # NB: self._value.__lt__(other) will not work for [int] < [float].
    return self._value < other

# Install simple overrides. This list could certainly be more exhaustive but
# there seem to be enough quirks with proxy objects it isn't obvious if a full
# list would be a good idea.
def _make_method(name: str) -> Callable:
  def method(self: Any, *args: Any, **kwargs: Any) -> Any:
    if hasattr(self._value, name):
      return getattr(self._value, name)(*args, **kwargs)
    return NotImplemented
  return method
for method in ['__eq__']:
  setattr(call, method, _make_method(method))


class calling(call):
  """Returns an object which has yet-to-be called."""
  def __call__(self, *args: Any, **kwargs: Any) -> None:
    if args or kwargs:
      raise NotImplementedError()
    return self._value


class look_like(equal):
  def __init__(self, expected: str, remove_comments: bool = False) -> None:
    self._remove_comments = remove_comments
    super(look_like, self).__init__(self._clean(expected))

  def _match(self, subject: str) -> tuple:
    cleaned = self._clean(subject)
    success, _ = super(look_like, self)._match(cleaned)
    error_lines = ['looks like:'] + textwrap.indent(cleaned, ' ').split('\n')
    return success, error_lines

  def _clean(self, s: str) -> str:
    if self._remove_comments:
      def sub(m: Match[str]) -> str:
        if m.group(2) is None:
          return m.group(1)
        return ''

      pattern = r'(\".*?\"|\'.*?\')|(\s*#[^\r\n]*$)'
      s = re.compile(pattern, re.MULTILINE | re.DOTALL).sub(sub, s)

    return textwrap.dedent(s.rstrip(' ').strip('\n'))


def path_values(root: Any, path: Iterable) -> str:
  """Traverse `root` following `path` and return repr result."""
  results = [repr(root)]
  cursor = root
  for c in path:
    cursor = cursor[c]
    results.append('%s = %r' % (c, cursor))
  return '\n'.join(results)


def mock_wrap(fn: Callable) -> Callable:
  return mock.Mock(wraps=fn)
