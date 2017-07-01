from data.logic.dsl import *
from spec.mamba import *

with description('solutions'):
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
      expect(str(self.model)).to(look_like("""
        assign:
          name["Andy"].occupation["analyst"] in {0,1}
          name["Bob"].age[11] in {0,1}
          occupation["analyst"].age[11] in {0,1}
          
        subject to:
          (name["Andy"].occupation["analyst"] == True)
          ((name["Bob"].age[11] + occupation["analyst"].age[11]) == 1)
      """))
