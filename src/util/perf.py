import contextlib
import random
import time
from typing import Any, Callable, Dict, List, NamedTuple, Union

_STATES = []
_ALL_PERFS = []
Variant = Union[str, int]
Implementation = Dict[Variant, Callable]
class ImplementationHooks(NamedTuple):
  before: Implementation
  body: Implementation
  after: Implementation


class Perf(object):
  def __init__(self, name: str, variants: Union[List[str], int] = 2) -> None:
    self._name = name
    if isinstance(variants, int):
      self._variants = list(range(1, variants + 1))
    else:
      self._variants = variants
    self._variants_map = {
      name: index for index, name in enumerate(self._variants)
    }
    self._timings = [(0, 0, 0)] * len(self._variants)
    self._parent = None
    _ALL_PERFS.append(self)

  def next_variant(self) -> Variant:
    return random.choice(self._variants)

  def child(self, name) -> 'Perf':
    result = Perf('%s: %s' % (self._name, name), self._variants)
    result._parent = self
    return result

  def increment(self, name: Variant, delta: float):
    if self._parent:
      self._parent.increment(name, delta)
    variant = self._variants_map[name]
    calls, elapsed, last = self._timings[variant]
    self._timings[variant] = (calls + 1, elapsed + delta, last)

  def before(self, name: Variant) -> Callable:
    return _Decorator(self).before(name)

  def profile(self, name: Variant) -> Callable:
    return _Decorator(self).profile(name)

  def after(self, name: Variant) -> Callable:
    return _Decorator(self).after(name)

  @contextlib.contextmanager
  def benchmark(self, name: Variant):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    self.increment(name, end - start)

  def __len__(self) -> int:
    return sum(calls for calls, _, _ in self._timings)

  def __str__(self) -> str:
    results = [self._name]
    if any(elapsed for _, elapsed, _ in self._timings):
      worst = min(
          calls / elapsed for calls, elapsed, _ in self._timings if elapsed)
    else:
      worst = 0
    for index, (calls, elapsed, last) in enumerate(self._timings):
      if elapsed:
        cps = calls / elapsed
        x = cps / worst
        results.append('%s: %.2f/s, %.2fx (%s calls, %.2fu)' % (
          self._variants[index], cps, x, calls, 1000 * elapsed))
      elif calls:
        results.append('%s: inf (%s calls)' % (
          self._variants[index], calls))
      else:
        results.append('%s: 0 (0 calls)' % (
          self._variants[index]))
    return '\n'.join(results)


def report() -> str:
  return '\n\n'.join(str(perf) for perf in _ALL_PERFS if perf)


def push() -> None:
  global _ALL_PERFS
  _STATES.append(_ALL_PERFS)
  _ALL_PERFS = []


def pop() -> None:
  global _ALL_PERFS
  _ALL_PERFS = _STATES.pop()


class _Decorator(object):
  def __init__(self, perf: Perf) -> None:
    self._perf = perf
    self._before_hooks = {}
    self._implementations = {}
    self._after_hooks = {}
    self._proxy = lambda *args, **kwargs: self._exec(args, kwargs)
    setattr(self._proxy, 'before', self.before)
    setattr(self._proxy, 'profile', self.profile)
    setattr(self._proxy, 'after', self.after)

  def _exec(self, args, kwargs) -> Any:
    variant = self._perf.next_variant()
    if variant in self._before_hooks:
      self._before_hooks[variant](*args, **kwargs)
    implementation = self._implementations[variant]
    start = time.perf_counter()
    result = implementation(*args, **kwargs)
    end = time.perf_counter()
    self._perf.increment(variant, end - start)
    if variant in self._after_hooks:
      self._after_hooks[variant](*args, **kwargs)
    return result

  def before(self, name: str) -> Callable:
    def setter(fn: Callable) -> Callable:
      self._before_hooks[name] = fn
      return self._proxy
    return setter

  def profile(self, name: str) -> Callable:
    def setter(fn: Callable) -> Callable:
      self._implementations[name] = fn
      return self._proxy
    return setter

  def after(self, name: str) -> Callable:
    def setter(fn: Callable) -> Callable:
      self._after_hooks[name] = fn
      return self._proxy
    return setter
