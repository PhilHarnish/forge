import numpy as np

from data.image import hexagonal_grid, image
from puzzle.constraints.image import hexagonal_grid_constraints, \
  identify_regions_constraints
from spec.mamba import *

with description('hexagonal_grid') as self:
  with before.each:
    self.image = image.Image(np.zeros((50, 50)))
    self.constraints = hexagonal_grid_constraints.HexagonalGridConstraints(
        self.image)
    self.constraints.update_active_for_method(
        identify_regions_constraints.Method.HEXAGONAL_GRID)
    self.grid = hexagonal_grid.HexagonalGrid(self.image, self.constraints)

  with it('returns divisions'):
    divisions = list(self.grid.get_slope_divisions())
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
    divisions = list(self.grid.get_slope_divisions())
    expect(divisions).to(have_len(edges))
