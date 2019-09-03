from typing import List

from puzzle.constraints import validator
from puzzle.constraints.image import identify_regions_constraints


class LinesClassifierConstraints(
    identify_regions_constraints.BaseRegionConstraints):
  """Constraints for lines_classifier.

  canny_aperture_px: int. Aperture size for cv2.Canny(). Valid values: 3, 5, 7.
    Smaller is faster, larger can produce noise.
  image_dilate_px: int. Number of pixels to dilate (enlarge) information.
  hough_lines_threshold_fractions: List[float]. Each float is the fraction of
    an image the line must pass through to be considered valid.
  hough_lines_minimum_lines: int. Minimum number of lines required for the set
    to be considered valid.
  angle_cluster_degrees: float. Maximum number of degrees two lines can be
    separated by and still be considered part of the same cluster.
  angle_resolution_degrees: float. Resolution used to detect lines in image.
  lines_sample_fraction: float. Filter and retain this fraction of Hough lines.
  required_divisions_ratio: float. Required fraction of divisions which must
    have lines present. E.g., with `0.5` half of the divisions must have lines.
  max_consecutive_missing: int. Limit to consecutive missing lines.
    0 forbids any missing lines.
  anchor_resolution_px: float. Resolution to use when determining if the
    algorithm's solution is considered unique. Large values produce quick but
    inferior results.
  division_distance_resolution_px: float. Resolution to use when determining if
    division distance (width) is considered unique. Large values produce quick
    but inferior results.
  """
  canny_aperture_px: validator.Option([3, 5, 7]) = 5
  image_dilate_px: validator.NumberInRange(min_value=0, max_value=10) = 3
  hough_lines_threshold_fractions: List[float] = [8/10, 2/3, 1/2, 1/3]
  hough_lines_minimum_lines: (
    validator.NumberInRange(min_value=0, max_value=100)) = 32
  angle_cluster_degrees: (
      validator.NumberInRange(min_value=0.0, max_value=29.9)) = 10
  angle_resolution_degrees: (
      validator.NumberInRange(min_value=0.0, max_value=29.9)) = 1.0
  lines_sample_fraction: (
      validator.NumberInRange(min_value=.50, max_value=1.0)) = 0.95
  required_divisions_ratio: (
      validator.NumberInRange(min_value=0.01, max_value=1.0)) = 0.70
  max_consecutive_missing: validator.NumberInRange(min_value=0) = 2
  anchor_resolution_px: (
      validator.NumberInRange(min_value=0.01, max_value=10.0)) = 2.0
  division_distance_resolution_px: (
      validator.NumberInRange(min_value=0.01, max_value=200.0)) = 85.0

  _method: identify_regions_constraints.Method = (
      identify_regions_constraints.Method.LINES_CLASSIFIER)
