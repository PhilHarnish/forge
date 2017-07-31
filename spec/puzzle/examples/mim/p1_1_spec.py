from data import warehouse
from puzzle.examples.mim import p1_1
from puzzle.problems import logic_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with _description('p1_1'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.puzzle = p1_1.get()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with description('solution'):
    with it('scores the source as a LogicProblem'):
      expect(logic_problem.LogicProblem.score(
          p1_1.SOURCE.split('\n'))).to(equal(1))

    with it('identifies puzzle type'):
      problems = self.puzzle.problems()
      expect(problems).to(have_len(1))
      problem = problems[0]
      expect(problem).to(be_a(logic_problem.LogicProblem))

    with _it('models puzzle'):
      model = logic_problem._model(p1_1.SOURCE.split('\n'))
      model.add(model.dimension_constraints())
      print(str(model))

    with it('exports a solution'):
      problem = self.puzzle.problems()[0]
      expect(problem.solution).to(look_like(
          p1_1.SOLUTION))
      solutions = problem.solutions()
      if len(solutions) > 1:
        for solution in solutions:
          print(solution)
      expect(solutions).to(have_len(1))
