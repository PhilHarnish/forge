from data.logic import _predicates
from spec.mamba import *

with description('_predicates'):
  with it('handles empty input'):
    expect(calling(_predicates.Predicates, [])).not_to(raise_error)

  with it('handles simple input'):
    expect(calling(_predicates.Predicates, [1, 2, 3])).not_to(raise_error)

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
