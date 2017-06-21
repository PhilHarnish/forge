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

  with description('solution'):
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
        name, age = variable_name.split('x')
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
      expect(self.subject.solution()).to(equal({
        'Andyx10': 0, 'Bobx10': 0, 'Cathyx10': 1,
        'Andyx11': 1, 'Bobx11': 0, 'Cathyx11': 0,
        'Andyx12': 0, 'Bobx12': 1, 'Cathyx12': 0,
      }))
