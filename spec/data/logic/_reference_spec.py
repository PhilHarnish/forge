import Numberjack

from data.logic import _reference
from spec.mamba import *

with description('_reference.Reference'):
  with before.each:
    self.model = mock.Mock(
        __name__='_model._Model',
        get_variables=lambda *args: Numberjack.Variable(),
        side_effect=lambda *args: [a.ident for a in args]
    )

  with description('ValueReference constructor'):
    with it('handles simple input'):
      expect(calling(_reference.ValueReference, self.model, 1)).not_to(
          raise_error)

  with description('Reference constructor'):
    with it('handles simple input'):
      expect(calling(_reference.ValueReference, self.model, {})).not_to(
          raise_error)
      expect(calling(_reference.ValueReference, self.model, False)).not_to(
          raise_error)

  with description('ValueReference operator overloading'):
    with before.each:
      self.subject = _reference.ValueReference(self.model, 5)

    with it('supports +, -, >, < with primitive'):
      expect(self.subject + 1).to(equal(6))
      expect(self.subject - 1).to(equal(4))
      expect(self.subject > 1).to(equal(True))
      expect(self.subject < 1).to(equal(False))

    with it('supports +, -, >, < with another ValueReference'):
      ref = _reference.ValueReference(self.model, 1)
      expect(self.subject + ref).to(equal(6))
      expect(self.subject - ref).to(equal(4))
      expect(self.subject > ref).to(equal(True))
      expect(self.subject < ref).to(equal(False))

  with description('Reference operator overloading'):
    with it('merges two References under equality'):
      a = _reference.Reference(self.model, {'key_a': 'value_a'})
      b = _reference.Reference(self.model, {'key_b': 'value_b'})
      c = a == b
      expect(c).to(be_a(_reference.Reference))
      expect(c._constraints).to(equal({
        'key_a': 'value_a',
        'key_b': 'value_b',
      }))

    with it('merges two Referenes under equality'):
      a = _reference.Reference(self.model, {'key_a': 'value_a'})
      b = _reference.Reference(self.model, {'key_b': 'value_b'})
      c = a != b
      expect(c).to(be_a(Numberjack.Predicate))
      expect(str(c)).to(equal('(x == False)'))

  with description('value'):
    with it('returned from ValueReference matches input'):
      expect(_reference.ValueReference(self.model, 11).value()).to(equal(11))

    with it('returned from Reference matches input if under-constrained'):
      expect(_reference.Reference(self.model, {
        'age': 11,
      }).value()).to(equal(11))

    with it('returns Numberjack.Variable for 2 constraints'):
      value = _reference.Reference(self.model, {
        'age': 11,
        'name': 'andy',
      }).value()
      expect(value).to(be_a(Numberjack.Variable))

  with description('modeling'):
    with it('raises exception when modeled'):
      value = _reference.Reference(self.model, {})
      expect(calling(self.model, value)).to(raise_error)
