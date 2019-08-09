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

    with it('adds dependencies later'):
      s = step.Step()
      s.depends_on(step.Step())
      expect(s).to(have_len(2))

    with it('tracks a tree of dependencies'):
      left_left = step.Step()
      left_right = step.Step()
      left = step.Step([left_left, left_right])
      right = step.Step()
      root = step.Step([left, right])
      resolution_order = list(root.resolution_order())
      expect(len(resolution_order)).to(equal(5))
      expect(resolution_order).to(equal([
        left_left,
        left_right,
        left,
        right,
        root,
      ]))

  with description('debug data'):
    with it('does not return data by default'):
      expect(calling(step.Step().get_debug_data)).to(raise_error)
