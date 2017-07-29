import Numberjack

from data.logic import _predicates
from spec.mamba import *

with description('_predicates'):
  with it('handles empty input'):
    expect(calling(_predicates.Predicates, [])).not_to(raise_error)

  with it('handles simple input'):
    expect(calling(_predicates.Predicates, [1, 2, 3])).not_to(raise_error)

  with it('resists nesting'):
    o = _predicates.Predicates([13])
    for _ in range(5):
      o = _predicates.Predicates(o)
    expect(o).to(have_len(1))
    expect(o[0]).to(equal(13))

  with it('handles == operator overloading'):
    predicates = _predicates.Predicates([1, 2, 3]) == 2
    expect(predicates).to(equal([False, True, False]))

  with it('handles != operator overloading'):
    predicates = _predicates.Predicates([1, 2, 3]) != 2
    expect(predicates).to(equal([True, False, False]))

  with it('handles - operator overloading'):
    predicates = _predicates.Predicates([1, 2, 3]) - 2
    expect(predicates).to(equal([-1, 0, 1]))

  with it('handles + operator overloading'):
    predicates = _predicates.Predicates([1, 2, 3]) + 2
    expect(predicates).to(equal([-1, 0, 1]))

  with it('handles < operator overloading'):
    predicates = _predicates.Predicates([1, 2, 3]) < 2
    expect(predicates).to(equal([True, False, False]))
    predicates = _predicates.Predicates([1, 2, 3]) <= 2
    expect(predicates).to(equal([True, True, False]))

  with it('handles > operator overloading'):
    predicates = _predicates.Predicates([1, 2, 3]) > 2
    expect(predicates).to(equal([False, False, True]))
    predicates = _predicates.Predicates([1, 2, 3]) > 2
    expect(predicates).to(equal([False, True, True]))

  with it('handles | operator overloading'):
    predicates = _predicates.Predicates([1, 2, 3]) | 2
    expect(predicates).to(equal([3, 2, 3]))

  with it('handles ^ operator overloading'):
    predicates = _predicates.Predicates([1, 2, 3]) ^ 2
    expect(predicates).to(equal([1, 0, 1]))

  with description('str'):
    with it('produces strings for empty predicates'):
      predicates = _predicates.Predicates([])
      expect(str(predicates)).to(equal(''))

    with it('produces strings for single predicates'):
      predicates = _predicates.Predicates(['first expression'])
      expect(str(predicates)).to(equal('first expression'))

    with it('produces strings for multiple predicates'):
      predicates = _predicates.Predicates(['first', 'second'])
      expect(str(predicates)).to(equal('first\nsecond'))

    with it('produces Numberjack expressions'):
      x = Numberjack.Variable('var')
      expect(str(x)).to(equal('var in {0,1}'))
      Numberjack.Model(x == True).load('Mistral').solve()
      expect(str(x)).to(equal('1'))

  with description('value'):
    with it('refuses to get value for multiple predicates'):
      predicates = _predicates.Predicates([])
      expect(calling(predicates.value)).to(raise_error(AssertionError))

    with it('returns primitive values'):
      predicates = _predicates.Predicates([13])
      expect(predicates.value()).to(equal(13))

    with it('returns Numberjack leaves'):
      x = Numberjack.Variable(15)
      m = Numberjack.Model()
      m.add(x == 14)
      m.load('Mistral').solve()
      predicates = _predicates.Predicates([x])
      expect(predicates.value()).to(equal(14))

    with it('returns Numberjack sub-expressions'):
      x = Numberjack.Variable(15)
      m = Numberjack.Model()
      m.add(x == 14)
      m.load('Mistral').solve()
      predicates = _predicates.Predicates([x == 14])
      expect(predicates.value()).to(equal(True))

  with description('priorities'):
    with before.all:
      FAIL = {}
      self.FAIL = FAIL


      class _Value(object):
        def __init__(self, value):
          self._value = value


      class _HighPriority(_Value):
        def __eq__(self, other):
          return self._value == other._value

        def __add__(self, other):
          return self._value + other._value


      class _LowPriority(_Value):
        def __eq__(self, other):
          return FAIL

        def __add__(self, other):
          return FAIL


      self.patcher = mock.patch.object(_predicates, '_LOWER_PRIORITY', (
        _LowPriority,
      ))

      self.patcher.start()
      self.bad_value = _LowPriority(5)
      self.good_value = _HighPriority(5)

    with after.all:
      self.patcher.stop()

    with it('normally prefers left operand'):
      expect(self.bad_value == self.good_value).to(be(self.FAIL))

    with it('succeeds when operands are flipped'):
      expect(self.good_value == self.bad_value).to(be_true)

    with it('changes precedence as Predicates'):
      expect(_predicates.Predicates([self.bad_value]) == self.good_value).to(
          equal([True]))
