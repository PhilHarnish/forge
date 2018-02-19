import itertools

from spec.mamba import *
from util import perf

_CLOCK = itertools.count()
_perf_counter_patch = mock.patch(
    'util.perf.time.perf_counter', side_effect=lambda: next(_CLOCK))


with description('perf'):
  with before.each:
    self._patch = _perf_counter_patch.start()

  with after.each:
    _perf_counter_patch.stop()

  with it('constructs for 2 variants, by default'):
    expect(calling(perf.Head2Head)).not_to(raise_error)
    expect(str(perf.Head2Head())).to(look_like("""
        #0: 0 (0 calls)
        #1: 0 (0 calls)
    """))

  with it('benchmarks variable number of variants'):
    b = perf.Head2Head(4)
    expect(str(b)).to(look_like("""
        #0: 0 (0 calls)
        #1: 0 (0 calls)
        #2: 0 (0 calls)
        #3: 0 (0 calls)
    """))

  with it('increments time with start & end calls'):
    b = perf.Head2Head(1)
    b.start()
    b.end()
    expect(str(b)).to(equal('#0: 1.0/s (1 calls)'))
