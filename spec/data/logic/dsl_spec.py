import collections

from data.logic.dsl import *
from spec.mamba import *

with description('dsl'):
  with before.each:
    self.dimensions = DimensionFactory()
    self.model = Model(self.dimensions)

  with it('defines dimensions'):
    (Andy, Bob, Cathy) = name = self.dimensions(name=['Andy', 'Bob', 'Cathy'])
    (CEO, Project_Manager, Analyst) = occupation = self.dimensions(
        occupation=['CEO', 'Project Manager', 'analyst'])
    (_10, _11, _12) = age = self.dimensions(age=[10, 11, 12])
    expect(self.dimensions.dimensions()).to(have_len(3))

  with description('with setup'):
    with before.each:
      (self.Andy, self.Bob, self.Cathy) = self.name = self.dimensions(
          name=['Andy', 'Bob', 'Cathy'])
      (self.CEO, self.Project_Manager, self.Analyst) = self.occupation = (
        self.dimensions(occupation=['CEO', 'Project Manager', 'analyst']))
      (self._10, self._11, self._12) = self.age = self.dimensions(
          age=[10, 11, 12])

    with it('accumulates constraints'):
      self.model(self.Andy == self.Analyst)
      expect(self.model.constraints).to(have_len(1))

    with it('supports diverse constraints'):
      self.model(self.Andy.occupation == self.Analyst)
      self.model((11 == self.Bob.age) ^ (11 == self.Analyst.age))
      self.model(self.CEO.age + 2 == self.Andy.age)
      expect(str(self.model)).to(look_like("""
        assign:
          name["Andy"].occupation["analyst"] in {0,1}
          name["Bob"].age in {10..12}
          occupation["analyst"].age in {10..12}
          name["Andy"].age in {10..12}
          occupation["CEO"].age in {10..12}
        
        subject to:
          (name["Andy"].occupation["analyst"] == True)
          (((name["Bob"].age == 11) + (occupation["analyst"].age == 11)) == 1)
          (name["Andy"].age == (occupation["CEO"].age + 2))
      """))

  with description('2D solutions'):
    with before.each:
      (self.Andy, self.Bob, self.Cathy) = self.name = self.dimensions(
          name=['Andy', 'Bob', 'Cathy'])
      (self._10, self._11, self._12) = self.age = self.dimensions(
          age=[10, 11, 12])

    with it('volunteers a valid solution without any context'):
      name_counter = collections.Counter()
      age_counter = collections.Counter()
      solver = self.model.load('Mistral')
      solver.solve()
      expect(str(solver)).to(look_like("""
           name | age
           Andy |  10
            Bob |  11
          Cathy |  12
      """))

    with it('finds correct solution with constraints'):
      # Force Bob == 12.
      self.model(~self.Andy[12])
      self.model(~self.Cathy[12])
      # Force Cathy == 10
      self.model(~self.name['Cathy'][11])
      expect(str(self.model)).to(look_like("""
          assign:
            name["Andy"].age in {10..12}
            name["Cathy"].age in {10..12}
         
          subject to:
            ((1 - (name["Andy"].age == 12)) == True)
            ((1 - (name["Cathy"].age == 12)) == True)
            ((1 - (name["Cathy"].age == 11)) == True)
      """))
      solver = self.model.load('Mistral')
      expect(solver.solve()).to(be_true)
      expect(str(solver)).to(look_like("""
           name | age
           Andy |  11
            Bob |  12
          Cathy |  10
      """))

    with it('finds solutions with reified dimension inequalities'):
      # Force Andy between Cathy and Bob.
      self.model(self.name['Andy']['age'] > self.name['Cathy']['age'])
      self.model(self.name['Andy']['age'] < self.name['Bob']['age'])
      solver = self.model.load('Mistral')
      expect(solver.solve()).to(be_true)
      expect(str(solver)).to(look_like("""
           name | age
           Andy |  11
            Bob |  12
          Cathy |  10
      """))

    with it('finds solutions with reified dimension offsets'):
      # Cathy = Bob - 2.
      self.model(self.name['Cathy']['age'] == self.name['Bob']['age'] - 2)
      solver = self.model.load('Mistral')
      expect(solver.solve()).to(be_true)
      expect(str(solver)).to(look_like("""
           name | age
           Andy |  11
            Bob |  12
          Cathy |  10
      """))

    with it('support for abs()'):
      self.model(abs(self.name['Andy']['age'] - self.name['Cathy']['age']) == 2)
      self.model(self.name['Cathy']['age'] > self.name['Andy']['age'])
      solver = self.model.load('Mistral')
      expect(solver.solve()).to(be_true)
      expect(str(solver)).to(look_like("""
           name | age
           Andy |  10
            Bob |  11
          Cathy |  12
      """))
      expect(solver.solve()).to(be_false)

  with description('3D solutions'):
    with before.each:
      (self.Andy, self.Bob, self.Cathy) = self.name = self.dimensions(
          name=['Andy', 'Bob', 'Cathy'])
      (self.CEO, self.Project_Manager, self.Analyst) = self.occupation = (
        self.dimensions(occupation=['CEO', 'Project Manager', 'Analyst']))
      (self._10, self._11, self._11) = self.age = self.dimensions(
          age=[10, 11, 11])

    with it('volunteers a valid solution without any context'):
      seen = collections.Counter()
      solver = self.model.load('Mistral')
      solver.solve()
      for variable_name, value in self.model._variable_cache.items():
        x, y = variable_name.split('.')
        if value.get_value():
          seen[x] += 1
          seen[y] += 1
      # Each value is part of 2 tables except for 11 which appears 2x.
      expect(seen).to(equal({
        'name["Andy"]': 2, 'name["Bob"]': 2, 'name["Cathy"]': 2,
        'occupation["CEO"]': 2, 'occupation["Project Manager"]': 2,
        'occupation["Analyst"]': 2,
        'age[10]': 2, 'age[11]': 4,
      }))

    with it('produces a correct solution with constraints'):
      # CEO is not the youngest.
      self.model(self.CEO['age'] >= self.Project_Manager['age'])
      self.model(self.CEO['age'] >= self.Analyst['age'])
      # Andy is a year younger than Bob.
      self.model(self.Andy['age'] + 1 == self.Bob['age'])
      # Cathy is older than the Project_Manager.
      self.model(self.Cathy['age'] > self.Project_Manager['age'])
      # Bob is either the CEO or the Project Manager.
      self.model(self.Bob['Analyst'] | self.Bob['Project Manager'])
      solver = self.model.load('Mistral')
      expect(solver.solve()).to(be_true)
      expect(str(solver)).to(look_like("""
           name |      occupation | age
           Andy | Project Manager |  10
            Bob |         Analyst |  11
          Cathy |             CEO |  11
      """))
      # Verify there are no other solutions.
      expect(solver.solve()).to(be_false)

    with it('infers a solution despite duplicates'):
      # Cathy is CEO (constrain the two values with cardinality of 1).
      self.model(self.Cathy == self.CEO)
      # CEO is older (constrains CEO to one of the 11 values).
      self.model(self.CEO.age > self.Project_Manager.age)
      solver = self.model.load('Mistral')
      solutions = []
      while solver.solve():
        solutions.append(str(solver))
      solutions = list(sorted(solutions))
      expected_solutions = [
        """
           name |      occupation | age
           Andy |         Analyst |  11
            Bob | Project Manager |  10
          Cathy |             CEO |  11
        """,
        """
           name |      occupation | age
           Andy | Project Manager |  10
            Bob |         Analyst |  11
          Cathy |             CEO |  11
        """,
      ]
      expect(solutions).to(have_len(len(expected_solutions)))
      for solution, expected in zip(solutions, expected_solutions):
        expect(solution).to(look_like(expected))

    with it('models additional variables'):
      # Cathy is CEO (constrain the two values with cardinality of 1).
      self.model(self.Cathy == self.CEO)
      # CEO is older (constrains CEO to one of the 11 values).
      self.model(self.CEO.age > self.Project_Manager.age)
      ceo_is_old = variable('ceo_is_old')
      self.model(ceo_is_old == (self.CEO == self._11))
      expect(str(self.model)).to(look_like("""
      assign:
        name["Cathy"].occupation["CEO"] in {0,1}
        occupation["CEO"].age[10] in {0,1}
        occupation["CEO"].age[11] in {0,1}
        occupation["Project Manager"].age[10] in {0,1}
        occupation["Project Manager"].age[11] in {0,1}
        ceo_is_old in {0,1}
     
      subject to:
        (name["Cathy"].occupation["CEO"] == True)
        ((10*occupation["CEO"].age[10] + 11*occupation["CEO"].age[11]) > (10*occupation["Project Manager"].age[10] + 11*occupation["Project Manager"].age[11]))
        (occupation["CEO"].age[11] == ceo_is_old)
      """))
