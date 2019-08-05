from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import cv2
import numpy as np

from data.convert import repr_format
from data.image import coloring, utils

MutationDecorator = Callable[[Callable], Callable]
MutationFn = Callable[..., 'Image']
Mutation = Tuple[str, Tuple, Dict[str, Any]]
MutationSpec = Union[str, Mutation]
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

  @mutation(deps=['normalize',])
  def crop(self, border_color: np.ndarray) -> 'Image':
    utils.crop(self._src, border_color)
    return self

  @mutation(deps=['normalize',])
  def enhance(self) -> 'Image':
    coloring.enhance(self._src, out=self._src)
    return self

  def fork(self) -> 'Image':
    return Image(self._src.copy(), self)

  @mutation(deps=['normalize',])
  def grayscale(self) -> 'Image':
    cv2.cvtColor(self._src, cv2.COLOR_BGR2GRAY, dst=self._src)
    return self

  @mutation()
  def invert(self) -> 'Image':
    np.bitwise_not(self._src, out=self._src)
    return self

  @mutation()
  def normalize(self) -> 'Image':
    self._src = coloring.normalize(self._src)
    return self

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
