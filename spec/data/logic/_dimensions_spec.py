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

    with it('supports 3+ dimensions'):
      expect(calling(_dimensions._Dimensions, {
        'name': ['Andy', 'Bob', 'Cathy'],
        'age': [10, 11, 12],
        'occupation': ['CEO', 'Accountant', 'Analyst'],
      })).not_to(raise_error)

  with description('iterating 2D'):
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
        name, age = variable.name().split('_')
        expect(name).to(be_one_of('Andy', 'Bob', 'Cathy'))
        expect(age).to(be_one_of('10', '11', '12'))

    with it('should support slicing one dimension'):
      variables = self.subject['Andy'].values()
      expect(variables).to(have_len(3))
      for variable in variables:
        expect(variable).to(be_a(Numberjack.Variable))
        name, age = variable.name().split('_')
        expect(name).to(be_one_of('Andy'))
        expect(age).to(be_one_of('10', '11', '12'))

    with it('should support slicing multiple dimensions'):
      variables = self.subject['Andy'][10].values()
      expect(variables).to(have_len(1))
      variable = variables[0]
      expect(variable).to(be_a(Numberjack.Variable))
      name, age = variable.name().split('_')
      expect(name).to(equal('Andy'))
      expect(age).to(equal('10'))

    with it('should raise exception for impossible slices'):
      andy = self.subject['Andy']
      expect(lambda: andy['Bob']).to(raise_error(KeyError))

  with description('iterating 3D'):
    with before.each:
      # OrderedDict used to ensure storage_order is consistent.
      self.subject = _dimensions._Dimensions(collections.OrderedDict([
        ('name', ['Andy', 'Bob', 'Cathy']),
        ('age', [10, 11, 12]),
        ('occupation', ['CEO', 'Accountant', 'Analyst']),
      ]))

    with it('returns all variables by default'):
      expect(self.subject.items()).to(have_len(9 * 3))

    with it('returns a slice of variables once 1 dimension is specified'):
      # 2 rows of length 3 + 1.
      expect(self.subject['Andy'].items()).to(have_len(3 * 2))

    with it('returns a slice of variables matching criteria'):
      for result in self.subject['Andy'].values():
        expect(result.name()).to(contain('Andy'))

  with description('reifying 2D dimensions'):
    with before.each:
      # OrderedDict used to ensure storage_order is consistent.
      self.subject = _dimensions._Dimensions(collections.OrderedDict([
        ('name', ['Andy', 'Bob', 'Cathy']),
        ('age', [10, 11, 12]),
      ]))

    with it('should require an existing constraint'):
      expect(lambda: self.subject['age']).to(raise_error(KeyError))

    with it('requires reified dimension have integer values'):
      expect(lambda: self.subject[10]['name']).to(
          raise_error(NotImplementedError))

    with it('produces a reified dimension when valid'):
      dimension = self.subject['Andy']['age']
      expect(dimension).to(be_a(Numberjack.Predicate))

  with description('reifying 3D dimensions'):
    with before.each:
      # OrderedDict used to ensure storage_order is consistent.
      self.subject = _dimensions._Dimensions(collections.OrderedDict([
        ('name', ['Andy', 'Bob', 'Cathy']),
        ('age', [10, 11, 12]),
        ('occupation', ['CEO', 'Accountant', 'Analyst']),
      ]))

    with it('should reify age for Andy'):
      expect(lambda: self.subject['Andy']['age']).not_to(raise_error)

    with it('produce a valid predicate'):
      dimension = self.subject['Andy']['age']
      expect(dimension).to(be_a(Numberjack.Predicate))

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
