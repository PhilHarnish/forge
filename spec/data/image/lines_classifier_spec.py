import numpy as np

from data.image import image, lines_classifier
from puzzle.constraints.image import lines_classifier_constraints
from spec.mamba import *

with description('lines_classifier') as self:
  with before.each:
    self.source = image.Image(np.zeros((3, 3)))
    self.constraints = lines_classifier_constraints.LinesClassifierConstraints()

  with it('constructs without error'):
    expect(calling(
        lines_classifier.LinesClassifier, self.source, self.constraints)
    ).not_to(raise_error)
