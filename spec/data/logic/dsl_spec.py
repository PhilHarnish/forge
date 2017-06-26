from data.logic.dsl import *
from spec.mamba import *

with description('solutions'):
  with before.each:
    self.dimensions = DimensionFactory()
    self.model = Model(self.dimensions)

  with it('defines dimensions'):
    (Andy, Bob, Cathy) = name = self.dimensions(name=['Andy', 'Bob', 'Cathy'])
    (CEO, Project_Manager, analyst) = occupation = self.dimensions(
        occupation=['CEO', 'Project Manager', 'analyst'])
    (_10, _11, _12) = age = self.dimensions(age=[10, 11, 12])
