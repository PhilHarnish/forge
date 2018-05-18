from data.graph.multi import multi_iter, multi_state
from spec.mamba import *


A = [
  # Weighted words: (a10, 1.0), (a09, 0.9), (a08, 0.8).
  (multi_state.BLANK, ('a%02d' % v, v/10)) for v in range(10, 7, -1)
]
B_DOWN = [
  # State: {b: 10}, {b: 9}, ... {b: 6}.
  # Weighted words: (b10, 1.0), (b09, 0.9), ... (b01, 0.6).
  (multi_state.State({'b': v}), ('b%02d' % v, v/10)) for v in range(10, 5, -1)
]
B_UP = [
  # State: {b: 6}, {b: 7}, ... {b: 10}.
  # Weighted words: (b06, 1.0), (b07, 0.9), ... (b10, 0.6).
  (
    multi_state.State({'b': (11 - v) + 5}),
    ('b%02d' % v, v/10)
  ) for v in range(10, 5, -1)
]
B_DOWN_ALTERNATE = [
  # State: BLANK, {b: 9}, BLANK, {b: 7}, BLANK, ... {b: 6}.
  # Weighted words: (b10, 1.0), (b09, 0.9), ... (b06, 0.6).
  (
    multi_state.State({'b': v}) if v % 2 else multi_state.BLANK,
    ('b%02d' % v, v / 10)
  ) for v in range(10, 0, -1)
]


with description('multi_iter'):
  with it('yields empty list for empty input'):
    expect(list(multi_iter.multi_iter([]))).to(have_len(0))

  with it('yields input for single stream'):
    expect(list(multi_iter.multi_iter([A]))).to(equal([
      (state, (word,)) for state, word in A
    ]))

  with it('yields input for two streams'):
    results = list(multi_iter.multi_iter([A, A]))
    expect(results).to(equal([
      (multi_state.BLANK, (('a10', 1.0), ('a10', 1.0))),
      (multi_state.BLANK, (('a10', 1.0), ('a09', 0.9))),
      (multi_state.BLANK, (('a09', 0.9), ('a10', 1.0))),
      (multi_state.BLANK, (('a09', 0.9), ('a09', 0.9))),
      (multi_state.BLANK, (('a10', 1.0), ('a08', 0.8))),
      (multi_state.BLANK, (('a08', 0.8), ('a10', 1.0))),
      (multi_state.BLANK, (('a09', 0.9), ('a08', 0.8))),
      (multi_state.BLANK, (('a08', 0.8), ('a09', 0.9))),
      (multi_state.BLANK, (('a08', 0.8), ('a08', 0.8))),
    ]))
    weights = [a * b for _, ((_, a), (_, b)) in results]
    for a, b in zip(weights, weights[1:]):
      expect(a).to(be_above_or_equal(b))
