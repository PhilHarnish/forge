from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, \
  TypeVar, Union

import cv2
import numpy as np

from data.convert import repr_format
from data.image import coloring, component, utils

MutationFn = Callable[..., 'Image']
MutationDecorator = Callable[[MutationFn], MutationFn]
Mutation = Tuple[str, Tuple, Dict[str, Any]]
MutationSpec = Union[str, Mutation]
T = TypeVar('T')
Rho = float
Theta = float
PolarLine = Tuple[Rho, Theta]
HoughLine = List[PolarLine]
_EMPTY_ARGS = ()
_EMPTY_KWARGS = {}


def mutation(
    deps: Optional[Iterable[MutationSpec]] = None) -> MutationDecorator:
  deps = deps or []
  def decorator(method: MutationFn) -> MutationFn:
    method_name = method.__name__
    def method_wrapper(self: 'Image', *args, **kwargs) -> 'Image':
      for dep in deps:
        spec = _expand_mutation_spec(dep)
        if not self.has_mutation(spec):
          raise ValueError('%s must occur before %s' % (
            _repr_mutation_spec(*spec),
            _repr_mutation_spec(method_name, args, kwargs)))
      result = method(self, *args, **kwargs)
      self.add_mutation(method_name, args, kwargs)
      return result
    return method_wrapper
  return decorator


def computation(fn: Callable[[Any], T]) -> property:
  attr_name = '__cached__' + fn.__name__

  @property
  def wrapped(self: Any) -> T:
    revision, result = getattr(self, attr_name, (None, None))
    next_revision = len(self._mutations)
    if revision != next_revision:
      result = fn(self)
      setattr(self, attr_name, (next_revision, result))
    return result

  return wrapped


class Image(object):
  _src: np.ndarray
  _mutations: List[Mutation]
  _parent: 'Image'

  def __init__(self, src: np.ndarray, parent: 'Image' = None) -> None:
    self._src = src
    self._mutations = []
    self._parent = parent

  def add_mutation(
      self, name: str, args: Tuple[Any], kwargs: Dict[str, Any]) -> None:
    self._mutations.append((name, args, kwargs))

  def has_mutation(
      self, *mutations: MutationSpec, check_parents: bool = True) -> bool:
    for target in mutations:
      spec = _expand_mutation_spec(target)
      if _has_mutation(spec, self._mutations):
        continue
      elif (not check_parents or not self._parent or
            not self._parent.has_mutation(spec)):
        return False
    return True  # All mutations matched.

  def color_band(self, low: int, high: Optional[int] = None) -> np.ndarray:
    return coloring.color_band(self._src, low, high)

  @computation
  def bincount(self) -> np.ndarray:
    return np.bincount(self._src.ravel())

  @mutation()
  def canny(self, aperture_px: int) -> 'Image':
    cv2.Canny(self._src, 255, 255, self._src, aperture_px)
    return self

  @mutation(deps={'normalize'})
  def crop(self, border_color: np.ndarray) -> 'Image':
    # crop() creates a view and so edits are not "in-place".
    self._src = utils.crop(self._src, border_color)
    return self

  @mutation()
  def dilate(self, kernel: np.ndarray, iterations=1) -> 'Image':
    cv2.dilate(self._src, kernel, iterations=iterations, dst=self._src)
    return self

  @mutation(deps={'grayscale', 'invert', 'normalize'})
  def enhance(self) -> 'Image':
    coloring.enhance(self._src, out=self._src)
    return self

  @mutation()
  def erase_component(
      self,
      c: component.PositionedComponent,
      border_percentile: int,
      border_distance: int,
      border_size: int) -> 'Image':
    # Operate on the window component came from.
    padding = border_distance + border_size
    top, left = c.offset
    top_padding = min(padding, top)  # Use 0 if top is zero.
    left_padding = min(padding, left)
    source_height, source_width = self._src.shape[:2]
    height, width = c.source.shape[:2]
    right_padding = min(padding, source_width - (left + width))
    bottom_padding = min(padding, source_height - (top + height))
    # Slice the window from src.
    y1 = top - top_padding
    y2 = top + height + bottom_padding
    x1 = left - left_padding
    x2 = left + width + right_padding
    source_patch = self._src[y1:y2, x1:x2]
    # Copy component to a new img.
    expanded_height = y2 - y1
    expanded_width = x2 - x1
    expanded = np.zeros((expanded_height, expanded_width))
    expanded[
      top_padding:top_padding + height,
      left_padding:left_padding + width,
    ] = c.source
    # Identify border and fill pixels.
    border, fill = utils.outline_and_fill(
        expanded, border_distance, border_size)
    # Sample pixels.
    border_points = source_patch[np.nonzero(border)]
    p_low, p50 = np.percentile(
        border_points, (border_percentile, 50), interpolation='lower')
    if p_low == 0:
      color = 0
    else:
      color = p50
    # Assign the `fill` points the chosen `color`.
    source_patch[np.nonzero(fill)] = color
    return self

  def extract_rect(self, x: int, y: int, width: int, height: int) -> np.ndarray:
    sliced = self._src[y : y + height, x : x + width]
    sliced.setflags(write=False)
    return sliced

  def fork(self) -> 'Image':
    return Image(self._src.copy(), self)

  @mutation(deps=['normalize',])
  def grayscale(self) -> 'Image':
    # NB: `dst=self._src` appears to be insufficient for in-place edit.
    self._src = cv2.cvtColor(
        self._src, cv2.COLOR_BGR2GRAY, dst=self._src, dstCn=1)
    return self

  def hough_lines(
      self, angle_resolution: float, threshold: float) -> List[HoughLine]:
    return cv2.HoughLines(self._src, 1, angle_resolution, threshold, None, 0, 0)

  @mutation()
  def invert(self) -> 'Image':
    np.bitwise_not(self._src, out=self._src)
    return self

  @mutation()
  def mask(self, mask: np.ndarray) -> 'Image':
    self._src[mask == 0] = 0
    return self

  def mask_nonzero(self, mask: np.ndarray) -> int:
    return int(np.sum((self._src != 0) & (mask != 0)))

  @computation
  def nonzero(self) -> int:
    return np.count_nonzero(self._src)

  @mutation()
  def normalize(self) -> 'Image':
    self._src = coloring.normalize(self._src)
    return self

  @property
  def shape(self) -> Tuple[int, int]:
    return self._src.shape

  def __str__(self) -> str:
    stack = []
    node = self
    while node:
      stack.append(node)
      node = node._parent
    result = []
    for node in reversed(stack):
      if node._mutations:
        result.append('\n  .' + '\n  .'.join(
            _repr_mutation_spec(*spec) for spec in node._mutations))
      else:
        result.append('')
    return 'Image()' + '\n  .fork()'.join(result)

  def get_debug_data(
      self, replay_mutations: bool = False
  ) -> Union[np.ndarray, List[Tuple[str, np.ndarray]]]:
    if not replay_mutations:
      result = self._src.view()
      result.setflags(write=False)
      return result
    if not self._parent:
      raise ValueError('Original image information lost.')
    img = self._parent
    result = [('source', img.get_debug_data(replay_mutations=False))]
    for method, args, kwargs in self._mutations:
      img = getattr(img.fork(), method)(*args, **kwargs)
      result.append((method, img.get_debug_data(replay_mutations=False)))
    return result


def _expand_mutation_spec(target: MutationSpec) -> Mutation:
  if isinstance(target, tuple):
    return target
  return target, _EMPTY_ARGS, _EMPTY_KWARGS


def _has_mutation(target: Mutation, mutations: List[Mutation]) -> bool:
  method, args, kwargs = target
  for cmp_method, cmp_args, cmp_kwargs in mutations:
    if cmp_method != method:
      continue
    # Methods match.
    if args is _EMPTY_ARGS and kwargs is _EMPTY_KWARGS:
      return True
    # Args defined.
    raise NotImplementedError('Comparing args unsupported')
  return False  # No matches found.


def _repr_mutation_spec(
    method: str, args: tuple, kwargs: Dict[str, Any]) -> str:
  return '%s(%s)' % (method, repr_format.as_args(*args, **kwargs))
