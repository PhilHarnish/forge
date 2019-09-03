from puzzle.constraints.image import identify_regions_constraints, \
  lines_classifier_constraints
from spec.mamba import *

with description('lines_classifier_constraints') as self:
  with before.each:
    self.constraints = lines_classifier_constraints.LinesClassifierConstraints()

  with it('initially disables method constraints'):
    expect(self.constraints.is_modifiable('canny_aperture_px')).to(be_false)

  with description('initialized'):
    with before.each:
      self.constraints.update_active_for_method(
          identify_regions_constraints.Method.LINES_CLASSIFIER)

    with it('allows modifications after being enabled'):
      expect(self.constraints.is_modifiable('canny_aperture_px')).to(be_true)
