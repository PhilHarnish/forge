import time
from typing import Optional


class Head2Head(object):
  def __init__(self, variants: int = 2) -> None:
    self._idx = 0
    self._variants = variants
    self._running = None
    self._timings = [(0, 0, 0)] * variants

  def variant(self) -> int:
    return self._running or (self._idx % self._variants)

  def start(self, variant: Optional[int] = None) -> None:
    if self._running is not None:
      raise Exception('Already running variant %s' % self._running)
    if variant is None:
      variant = self.variant()
      self._idx += 1
    calls, elapsed, last = self._timings[variant]
    calls += 1
    self._running = variant
    self._timings[variant] = (calls, elapsed, time.perf_counter())

  def end(self, variant: Optional[int] = None) -> None:
    end = time.perf_counter()
    if self._running is None:
      raise Exception('Benchmark not running')
    if variant is None:
      variant = self._running
    elif variant != self._running:
      raise Exception('Specified variant %s but % is running instead' % (
        variant, self._running
      ))
    calls, elapsed, last = self._timings[variant]
    self._running = None
    self._timings[variant] = (calls, elapsed + (end - last), end)

  def __str__(self) -> str:
    results = []
    for variant, (calls, elapsed, last) in enumerate(self._timings):
      if elapsed:
        cps = calls / elapsed
        results.append('#%s: %s/s (%s calls)' % (variant, cps, calls))
      elif calls:
        results.append('#%s: inf (%s calls)' % (variant, calls))
      else:
        results.append('#%s: 0 (0 calls)' % variant)
    return '\n'.join(results)
