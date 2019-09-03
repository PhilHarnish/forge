import math
from typing import Dict, Iterable, Optional, Tuple, TypeVar

from data.image import image
from puzzle.constraints import constraints, validator
from puzzle.constraints.image import identify_regions_constraints
from util.geometry import np2d

Spec = Tuple[float, Tuple[int, int], int]


_UNDEFINED = (0, 0)
_DIMS = ('first', 'second', 'third', 'fourth', 'fifth', 'sixth')
_DIVISION_DIMS = tuple('n_divisions_%s' % dim for dim in _DIMS)
_ALL_DIM_FIELDS = set(_DIMS + _DIVISION_DIMS)
_Number = TypeVar('_Number', int, float)


class SlicedGridConstraints(
    identify_regions_constraints.BaseRegionConstraints):
  """Constraints for slicing an image into a grid.

  slices: int. Number of slices around center. Rectangular: 2. Hexagonal: 3.
  center: Point. Origin for slicing.
  degrees_offset: Degrees of rotation, counter-clockwise from East.
  first: Range. Beginning and end of the first dimension.
  second: Range. Beginning and end of the second dimension.
  third: Range. Beginning and end of the third dimension.
  fourth: Range. Beginning and end of the fourth dimension.
  fifth: Range. Beginning and end of the fourth dimension.
  sixth: Range. Beginning and end of the fourth dimension.
  n_divisions: int. Number of divisions across all dimensions.
  n_divisions_first: int. Divisions in first dimension. Overrides n_divisions.
  n_divisions_second: int. Divisions in second dimension. Overrides n_divisions.
  n_divisions_third: int. Divisions in third dimension. Overrides n_divisions.
  n_divisions_fourth: int. Divisions in fourth dimension. Overrides n_divisions.
  n_divisions_fifth: int. Divisions in fifth dimension. Overrides n_divisions.
  n_divisions_sixth: int. Divisions in sixth dimension. Overrides n_divisions.
  """
  slices: validator.Option([2, 3, 4, 6]) = 2
  center: validator.Point(0, 0) = _UNDEFINED
  degrees_offset: validator.NumberInRange(min_value=0, max_value=30) = 0
  first: validator.RangeInRange(min_value=0, max_value=0) = _UNDEFINED
  second: validator.RangeInRange(min_value=0, max_value=0) = _UNDEFINED
  third: validator.RangeInRange(min_value=0, max_value=0) = _UNDEFINED
  fourth: validator.RangeInRange(min_value=0, max_value=0) = _UNDEFINED
  fifth: validator.RangeInRange(min_value=0, max_value=0) = _UNDEFINED
  sixth: validator.RangeInRange(min_value=0, max_value=0) = _UNDEFINED
  n_divisions: Optional[validator.NumberInRange(min_value=1)] = 9
  n_divisions_first: validator.NumberInRange(min_value=1) = 9
  n_divisions_second: validator.NumberInRange(min_value=1) = 9
  n_divisions_third: validator.NumberInRange(min_value=1) = 9
  n_divisions_fourth: validator.NumberInRange(min_value=1) = 9
  n_divisions_fifth: validator.NumberInRange(min_value=1) = 9
  n_divisions_sixth: validator.NumberInRange(min_value=1) = 9

  _source: image.Image = None
  _annotations: Dict[str, validator.RangeInRange] = None

  _method: identify_regions_constraints.Method = (
      identify_regions_constraints.Method.SLICED_GRID)

  def __init__(self, source: image.Image) -> None:
    super().__init__()
    self._source = source
    self._annotations = {}
    self.set_source(source)

  def is_modifiable(self, key: str) -> bool:
    missing = _ALL_DIM_FIELDS - set(self._dims()) - set(self._division_dims())
    if key in missing:
      return False  # This field is N/A for the current number of slices.
    if not super().is_modifiable(key):
      return False
    if self.n_divisions is None:
      return True  # Anything can change.
    if key in self._division_dims():
      return False  # Cannot modify unless n_divisions is None.
    return True

  def set_source(self, source: image.Image) -> None:
    with self._allow_inactive_modifications():
      defaults = []
      old_source = self._source
      self._source = source
      height, width = source.shape[:2]
      self._annotations['center'] = validator.Point(width, height)
      if self.center is _UNDEFINED:
        self.center = (round(width / 2), round(height / 2))
      elif old_source:
        old_height, old_width = old_source.shape[:2]
        old_x, old_y = self.center
        defaults.append(
            ('center', (old_x, old_y, old_width, old_height, width, height)))
        for dim, args in defaults:
          setattr(self, dim, _preserve_proportions(*args))

  def get_specs(self) -> Iterable[Spec]:
    # Invert given radians to reduce confusion (clockwise -> counter-clockwise).
    offset = math.radians(-self.degrees_offset)
    for base_theta, dim, division_dim in zip(
        self._thetas(), self._dims(), self._division_dims()):
      if self.n_divisions is None:
        divisions = getattr(self, division_dim)
      else:
        divisions = self.n_divisions
      yield base_theta + offset, getattr(self, dim), divisions

  def _resolve_annotation(self, key: str) -> Optional[type]:
    if key in self._annotations:
      return self._annotations[key]
    return super()._resolve_annotation(key)

  def _before_change_event(
      self, event: constraints.ConstraintChangeEvent) -> None:
    if event.key in ('slices', 'center', 'degrees_offset'):
      with self._pause_events(flush=True):
        self._update_dims()

  def _update_dims(self) -> None:
    defaults = []
    height, width = self._source.shape[:2]
    base_theta = math.radians(-self.degrees_offset)
    cx, cy = self.center
    for dim, offset in zip(self._dims(), self._thetas()):
      old_value = getattr(self, dim)
      old_start, old_end = old_value
      old_annotation = self._annotations.get(dim)
      annotation = _range_annotation_for(width, height, cx, cy,
          base_theta + offset)
      new_min = annotation.min_value
      new_max = annotation.max_value
      self._annotations[dim] = annotation
      if old_annotation:
        old_min = old_annotation.min_value
        old_max = old_annotation.max_value
        defaults.append(
            (dim, _preserve_proportions(
                old_start, old_end, old_min, old_max, new_min, new_max)))
      elif old_value is _UNDEFINED:
        defaults.append((dim, (round(new_min / 2), round(new_max / 2))))
    with self._allow_inactive_modifications():
      with self._pause_events(flush=True):
        for dim, value in defaults:
          setattr(self, dim, value)

  def _dims(self) -> Iterable[str]:
    yield from _DIMS[:self.slices]

  def _division_dims(self) -> Iterable[str]:
    yield from _DIVISION_DIMS[:self.slices]

  def _thetas(self) -> Iterable[float]:
    size = math.pi / self.slices
    for i in range(self.slices):
      yield size * i


def _range_annotation_for(
    width: int, height: int, cx: int, cy: int, theta: float
) -> validator.RangeInRange:
  """Measure line length from (cx, cy) to width x height bounding box."""
  end = np2d.distance_to_bounding_box(width, height, cx, cy, theta)
  start = -np2d.distance_to_bounding_box(width, height, cx, cy, theta + math.pi)
  return validator.RangeInRange(round(start), round(end))


def _preserve_proportions(
    old_x: _Number, old_y: _Number,
    old_width: _Number, old_height: _Number,
    width: _Number, height: _Number,
) -> Tuple[_Number, _Number]:
  p_x = old_x / old_width
  p_y = old_y / old_height
  coerce = type(old_x)
  return coerce(p_x * width), coerce(p_y * height)
