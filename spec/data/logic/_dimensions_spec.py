import collections

import Numberjack

from data.logic import _dimensions
from spec.mamba import *

with description('_Dimensions'):
  with description('construction'):
    with it('should succeed with empty input'):
      expect(calling(_dimensions._Dimensions, {})).not_to(raise_error)

    with it('should succeed with 1 dimension'):
      expect(calling(_dimensions._Dimensions, {
        'name': ['Andy', 'Bob', 'Cathy'],
      })).not_to(raise_error)

    with it('should succeed with 2 dimensions'):
      expect(calling(_dimensions._Dimensions, {
        'name': ['Andy', 'Bob', 'Cathy'],
        'occupation': ['CEO', 'Accountant', 'Analyst'],
      })).not_to(raise_error)

    with it('should succeed with integer dimensions'):
      expect(calling(_dimensions._Dimensions, {
        'name': ['Andy', 'Bob', 'Cathy'],
        'age': [10, 11, 12],
      })).not_to(raise_error)

    with it('raises error when dimensions repeat'):
      expect(calling(_dimensions._Dimensions, {
        'name': ['Andy', 'Bob', 'Cathy'],
        'age': [10, 10, 10],
      })).to(raise_error)

    with it('does not support 3+ dimensions'):
      expect(calling(_dimensions._Dimensions, {
        'name': ['Andy', 'Bob', 'Cathy'],
        'age': [10, 10, 10],
        'occupation': ['CEO', 'Accountant', 'Analyst'],
      })).to(raise_error(NotImplementedError))

  with description('iterating'):
    with before.each:
      # OrderedDict used to ensure storage_order is consistent.
      self.subject = _dimensions._Dimensions(collections.OrderedDict([
        ('name', ['Andy', 'Bob', 'Cathy']),
        ('age', [10, 11, 12]),
      ]))

    with it('should return cross product variables by default'):
      variables = self.subject.values()
      expect(variables).to(have_len(9))
      for variable in variables:
        expect(variable).to(be_a(Numberjack.Variable))
        name, age = variable.name().split('x')
        expect(name).to(be_one_of('Andy', 'Bob', 'Cathy'))
        expect(age).to(be_one_of('10', '11', '12'))

    with it('should support slicing one dimension'):
      variables = self.subject['Andy'].values()
      expect(variables).to(have_len(3))
      for variable in variables:
        expect(variable).to(be_a(Numberjack.Variable))
        name, age = variable.name().split('x')
        expect(name).to(be_one_of('Andy'))
        expect(age).to(be_one_of('10', '11', '12'))

    with it('should support slicing multiple dimensions'):
      variables = self.subject['Andy'][10].values()
      expect(variables).to(have_len(1))
      variable = variables[0]
      expect(variable).to(be_a(Numberjack.Variable))
      name, age = variable.name().split('x')
      expect(name).to(equal('Andy'))
      expect(age).to(equal('10'))

    with it('should raise exception for impossible slices'):
      andy = self.subject['Andy']
      expect(lambda: andy['Bob']).to(raise_error(KeyError))

  with description('constraints'):
    with before.each:
      # OrderedDict used to ensure storage_order is consistent.
      self.subject = _dimensions._Dimensions(collections.OrderedDict([
        ('name', ['Andy', 'Bob', 'Cathy']),
        ('age', [10, 11, 12]),
      ]))

    with it('should export cardinality constraints by default'):
      constraints = self.subject.constraints()
      expect(constraints).to(have_len(6))
      for constraint in constraints:
        expect(constraint).to(be_a(Numberjack.Gcc))

    with description('assignment'):
      with it('should constrain single values'):
        before_len = len(self.subject.constraints())
        self.subject['Andy'][10] = False
        after_len = len(self.subject.constraints())
        expect(after_len - before_len).to(equal(1))

      with it('should constrain multiple values'):
        before_len = len(self.subject.constraints())
        self.subject['Andy'] = False
        after_len = len(self.subject.constraints())
        expect(after_len - before_len).to(equal(3))
