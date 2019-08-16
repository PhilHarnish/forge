import contextlib
import random
import time
from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional, \
  Tuple, Union

_STATES = []
_ALL_PERFS = []
Variant = Union[str, int]
Implementation = Dict[Variant, Callable]


class ImplementationHooks(NamedTuple):
  before: Implementation
  body: Implementation
  after: Implementation


class Perf(object):
  _name: str
  _parent: Optional['Perf']
  _variants: List[Variant]
  _variants_map: Dict[Variant, int]
  _decorators_map: Dict[Variant, '_Decorator']
  _before_hooks: Dict[Variant, Callable]
  _implementations: Dict[Variant, Callable]
  _after_hooks: Dict[Variant, Callable]
  _timings: List[Tuple[int, float, int]]
  _run_all: bool
  _return_variant: Optional[Variant]

  def __init__(
      self,
      name: str,
      variants: Union[List[str], int] = 2,
      run_all: bool = False,
      return_variant: Optional[Variant] = None,
  ) -> None:
    self._name = name
    self._parent = None
    if isinstance(variants, int):
      self._variants = list(range(1, variants + 1))
    else:
      self._variants = variants
    self._variants_map = {
      name: index for index, name in enumerate(self._variants)
    }
    self._decorators_map = {}
    self._before_hooks = {}
    self._implementations = {}
    self._after_hooks = {}
    self._timings = [(0, 0, 0)] * len(self._variants)
    self._run_all = run_all
    if return_variant is not None and not run_all:
      raise ValueError('return_variant requires run_all')
    self._return_variant = return_variant
    _ALL_PERFS.append(self)

  def next_variant(self) -> Variant:
    return random.choice(self._variants)

  def next_variants(self) -> Iterable[Variant]:
    if self._run_all:
      yield from self._variants
    else:
      yield random.choice(self._variants)

  def child(self, name) -> 'Perf':
    result = Perf('%s: %s' % (self._name, name), self._variants)
    result._parent = self
    return result

  def choose_result(self, results: Dict[Variant, Any]) -> Any:
    if self._return_variant is not None:
      return results[self._return_variant]
    sample = next(iter(results.values()))  # Choose value randomly.
    if not all(value == sample for value in results.values()):
      raise ValueError(
          'Results inconsistent (use return_variant kwarg to choose):\n%s' % (
              repr(results)))
    return sample

  def increment(self, name: Variant, delta: float):
    if self._parent:
      self._parent.increment(name, delta)
    variant = self._variants_map[name]
    calls, elapsed, last = self._timings[variant]
    self._timings[variant] = (calls + 1, elapsed + delta, last)

  def decorator(self, name: Variant) -> '_Decorator':
    if name not in self._decorators_map:
      self._decorators_map[name] = _Decorator(self)
    return self._decorators_map[name]

  def before(self, name: Variant) -> Callable:
    return self.decorator(name).before(name)

  def profile(self, name: Variant) -> Callable:
    return self.decorator(name).profile(name)

  def after(self, name: Variant) -> Callable:
    return self.decorator(name).after(name)

  def add_before_hook(self, name: Variant, fn: Callable) -> None:
    self._before_hooks[name] = fn

  def run_before_hook(self, name: Variant, args: list, kwargs: dict) -> None:
    if name in self._before_hooks:
      self._before_hooks[name](*args, **kwargs)

  def add_implementation(self, name: Variant, fn: Callable) -> None:
    self._implementations[name] = fn

  def run_implementation(self, name: Variant, args: list, kwargs: dict) -> Any:
    return self._implementations[name](*args, **kwargs)

  def add_after_hook(self, name: Variant, fn: Callable) -> None:
    self._after_hooks[name] = fn

  def run_after_hook(self, name: Variant, args: list, kwargs: dict) -> None:
    if name in self._after_hooks:
      self._after_hooks[name](*args, **kwargs)

  @contextlib.contextmanager
  def benchmark(self, name: Variant):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    self.increment(name, end - start)

  def __getitem__(self, item: Variant):
    return self.benchmark(item)

  def __len__(self) -> int:
    return sum(calls for calls, _, _ in self._timings)

  def __str__(self) -> str:
    results = [self._name]
    if any(elapsed for _, elapsed, _ in self._timings):
      worst = min(
          calls / elapsed for calls, elapsed, _ in self._timings if elapsed)
    else:
      worst = 0
    longest_name_length = max(len(str(s)) for s in self._variants)
    for index, (calls, elapsed, last) in sorted(
        enumerate(self._timings),
        key=lambda x: x[1][0] / (x[1][1] or float('inf'))):
      prefix = (
          '%s:' % self._variants[index]).ljust(longest_name_length + 1, ' ')
      if elapsed:
        cps = calls / elapsed
        x = cps / worst
        results.append('%s %.2f/s, %.2fx (%s calls, %.2fu)' % (
          prefix, cps, x, calls, 1000 * elapsed))
      elif calls:
        results.append('%s inf (%s calls)' % (prefix, calls))
      else:
        results.append('%s 0 (0 calls)' % prefix)
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
    self._proxy = lambda *args, **kwargs: self._exec(args, kwargs)
    setattr(self._proxy, 'before', self.before)
    setattr(self._proxy, 'profile', self.profile)
    setattr(self._proxy, 'after', self.after)

  def _exec(self, args, kwargs) -> Any:
    results = {}
    for variant in self._perf.next_variants():
      self._perf.run_before_hook(variant, args, kwargs)
      start = time.perf_counter()
      results[variant] = self._perf.run_implementation(variant, args, kwargs)
      end = time.perf_counter()
      self._perf.increment(variant, end - start)
      self._perf.run_after_hook(variant, args, kwargs)
    return self._perf.choose_result(results)

  def before(self, name: str) -> Callable:
    def setter(fn: Callable) -> Callable:
      self._perf.add_before_hook(name, fn)
      return self._proxy
    return setter

  def profile(self, name: str) -> Callable:
    def setter(fn: Callable) -> Callable:
      self._perf.add_implementation(name, fn)
      return self._proxy
    return setter

  def after(self, name: str) -> Callable:
    def setter(fn: Callable) -> Callable:
      self._perf.add_after_hook(name, fn)
      return self._proxy
    return setter
