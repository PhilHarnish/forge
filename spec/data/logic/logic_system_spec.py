import collections

from data.logic import logic_system
from spec.mamba import *

with description('LogicSystem'):
  with it('should succeed with empty input'):
    expect(calling(logic_system.LogicSystem, {})).not_to(raise_error)

  with it('should succeed with 2 dimensions'):
    expect(calling(logic_system.LogicSystem, {
      'name': ['Andy', 'Bob', 'Cathy'],
      'occupation': ['CEO', 'Accountant', 'Analyst'],
    })).not_to(raise_error)

  with description('2D solutions'):
    with before.each:
      # OrderedDict used to ensure storage_order is consistent.
      self.subject = logic_system.LogicSystem(collections.OrderedDict([
        ('name', ['Andy', 'Bob', 'Cathy']),
        ('age', [10, 11, 12]),
      ]))

    with it('volunteers a valid solution without any context'):
      name_counter = collections.Counter()
      age_counter = collections.Counter()
      for variable_name, value in self.subject.solution().items():
        name, age = variable_name.split('_')
        if value:
          name_counter[name] += 1
          age_counter[age] += 1
      expect(name_counter).to(equal({
        'Andy': 1,
        'Bob': 1,
        'Cathy': 1,
      }))
      expect(age_counter).to(equal({
        '10': 1,
        '11': 1,
        '12': 1,
      }))

    with it('finds correct solution with constraints'):
      d = self.subject._dimensions
      # Force Bob == 12.
      d['Andy'][12] = False
      d['Cathy'][12] = False
      # Force Cathy == 10
      d['Cathy'][11] = False
      expect(str(self.subject)).to(look_like("""
          Andy
          | Bob
          | | Cathy
              # 10
          #     11
            #   12
      """))

    with it('finds solutions with reified dimension inequalities'):
      d = self.subject._dimensions
      # Force Andy between Cathy and Bob.
      d.constrain(d['Andy']['age'] > d['Cathy']['age'])
      d.constrain(d['Andy']['age'] < d['Bob']['age'])
      expect(str(self.subject)).to(look_like("""
          Andy
          | Bob
          | | Cathy
              # 10
          #     11
            #   12
      """))
    with it('finds solutions with reified dimension offsets'):
      d = self.subject._dimensions
      # Cathy = Bob - 2.
      d.constrain(d['Cathy']['age'] == d['Bob']['age'] - 2)
      expect(str(self.subject)).to(look_like("""
          Andy
          | Bob
          | | Cathy
              # 10
          #     11
            #   12
      """))

  with description('3D solutions'):
    with before.each:
      # OrderedDict used to ensure storage_order is consistent.
      self.dimensions = collections.OrderedDict([
        ('name', ['Andy', 'Bob', 'Cathy']),
        ('age', [10, 11, 12]),
        ('occupation', ['CEO', 'Accountant', 'Analyst']),
      ])
      self.subject = logic_system.LogicSystem(self.dimensions)

    with it('volunteers a valid solution without any context'):
      seen = collections.Counter()
      for variable_name, value in self.subject.solution().items():
        x, y = variable_name.split('_')
        if value:
          seen[x] += 1
          seen[y] += 1
      # Each is "2" because each value is part of 2 tables.
      expect(seen).to(equal({
        'Andy': 2, 'Bob': 2, 'Cathy': 2,
        '10': 2, '11': 2, '12': 2,
        'CEO': 2, 'Accountant': 2, 'Analyst': 2,
      }))

    with it('produces a correct solution with constraints'):
      d = self.subject._dimensions
      # CEO is the oldest.
      d.constrain(d['CEO']['age'] > d['Accountant']['age'])
      d.constrain(d['CEO']['age'] > d['Analyst']['age'])
      # Andy is a year younger than Bob.
      d.constrain(d['Andy']['age'] + 1 == d['Bob']['age'])
      # Cathy is older than the Accountant.
      d.constrain(d['Cathy']['age'] > d['Accountant']['age'])
      # Bob is either the CEO or the accountant.
      d.constrain(d['Bob']['CEO'].value() | d['Bob']['Accountant'].value())
      expect(str(self.subject)).to(look_like("""
          Andy
          | Bob
          | | Cathy
          #     10
            #   11
              # 12
          Andy
          | Bob
          | | Cathy
              # CEO
            #   Accountant
          #     Analyst
          10
          | 11
          | | 12
              # CEO
            #   Accountant
          #     Analyst
      """))
