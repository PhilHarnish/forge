import numpy as np

from puzzle.problems import image_problem
from spec.mamba import *

with description('ImageProblem'):
  with it('ignores incorrect types'):
    expect(image_problem.ImageProblem.score([])).to(equal(0))
    expect(image_problem.ImageProblem.score([''])).to(equal(0))

  with it('accepts any ndarray'):
    expect(image_problem.ImageProblem.score(np.zeros((1, 1)))).to(be_above(0))

  with it('fully accepts uint8 ndarrays'):
    a = image_problem.ImageProblem.score(np.zeros((1, 1), dtype=np.uint8))
    expect(a).to(be_above(0))
