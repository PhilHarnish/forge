from puzzle.constraints import constraints, validator


class DecomposeConstraints(constraints.Constraints):
  erase_border_percentile: (
      validator.NumberInRange(min_value=0, max_value=100)) = 25
  erase_border_distance: (
      validator.NumberInRange(min_value=0, max_value=5)) = 2
  erase_border_size:(
      validator.NumberInRange(min_value=1, max_value=5)) = 2
  required_color_band_retention: (
      validator.NumberInRange(min_value=0.01, max_value=1.0)) = 0.5
