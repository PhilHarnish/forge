import itertools

import numpy as np

from data.image import image, sliced_grid
from puzzle.constraints.image import identify_regions_constraints, \
  sliced_grid_constraints
from spec.mamba import *

with description('sliced_grid') as self:
  with before.each:
    self.image = image.Image(np.zeros((50, 50)))
    self.constraints = sliced_grid_constraints.SlicedGridConstraints(
        self.image)
    self.constraints.update_active_for_method(
        identify_regions_constraints.Method.SLICED_GRID)
    self.constraints.slices = 3
    self.grid = sliced_grid.SlicedGrid(self.image, self.constraints)

  with it('returns divisions'):
    divisions = list(itertools.chain(*self.grid))
    edges = self.constraints.n_divisions + 1
    expect(divisions).to(have_len((edges * 3)))

  with it('returns different divisions if customized'):
    self.constraints.n_divisions = None
    self.constraints.n_divisions_first = 5
    self.constraints.n_divisions_second = 6
    self.constraints.n_divisions_third = 7
    edges = 3 + (
        self.constraints.n_divisions_first +
        self.constraints.n_divisions_second +
        self.constraints.n_divisions_third)
    divisions = list(itertools.chain(*self.grid))
    expect(divisions).to(have_len(edges))
