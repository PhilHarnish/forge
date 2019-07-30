from puzzle.steps import step
from spec.mamba import *

with description('step'):
  with description('constructor'):
    with it('constructs without error'):
      expect(calling(step.Step)).not_to(raise_error)

  with description('dependencies'):
    with it('starts out with zero dependencies'):
      s = step.Step()
      expect(s).to(have_len(1))

    with it('adds dependencies'):
      s = step.Step(dependencies=[step.Step()])
      expect(s).to(have_len(2))
