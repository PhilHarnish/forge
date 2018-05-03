import itertools

from spec.mamba import *
from util import perf

_CLOCK = itertools.count()
_perf_counter_patch = mock.patch(
    'util.perf.time.perf_counter', side_effect=lambda: next(_CLOCK))


with description('perf'):
  with before.each:
    self._patch = _perf_counter_patch.start()
    perf.push()

  with after.each:
    _perf_counter_patch.stop()
    perf.pop()

  with it('constructs for 2 variants, by default'):
    expect(calling(perf.Perf, 'test')).not_to(raise_error)
    expect(str(perf.Perf('test'))).to(look_like("""
        test
        1: 0 (0 calls)
        2: 0 (0 calls)
    """))

  with it('benchmarks variable number of variants'):
    b = perf.Perf('test', 4)
    expect(str(b)).to(look_like("""
        test
        1: 0 (0 calls)
        2: 0 (0 calls)
        3: 0 (0 calls)
        4: 0 (0 calls)
    """))

  with it('annotates functions'):
    b = perf.Perf('test', 1)
    @b.profile(1)
    def fn() -> None:
      pass
    fn()
    expect(str(b)).to(look_like("""
        test
        1: 1.00/s, 1.00x (1 calls, 1000.00u)
    """))

  with it('registers before and after functions'):
    b = perf.Perf('test', 1)
    called = []
    @b.before(1)
    def fn() -> None:
      called.append('before')
    @fn.profile(1)
    def fn() -> None:
      called.append('profile')
    @fn.after(1)
    def fn() -> None:
      called.append('after')
    fn()
    expect(called).to(equal(['before', 'profile', 'after']))

  with it('allows benchmarking code segments'):
    b = perf.Perf('test', 2)
    with b.benchmark(1):
      pass
    with b.benchmark(1):
      pass
    with b.benchmark(2):
      pass
    expect(str(b)).to(look_like("""
        test
        1: 1.00/s, 1.00x (2 calls, 2000.00u)
        2: 1.00/s, 1.00x (1 calls, 1000.00u)
    """))

