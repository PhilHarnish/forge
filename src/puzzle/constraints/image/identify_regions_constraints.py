import contextlib
import enum
from typing import Dict, Iterator

from puzzle.constraints import constraints


class Method(enum.Enum):
  LINES_CLASSIFIER = enum.auto()
  SLICED_GRID = enum.auto()


class BaseRegionConstraints(constraints.Constraints):
  _method: Method = None
  _active: bool = False
  _allow_inactive_modifications_semaphore: int = 0

  def get_method(self) -> Method:
    return self._method

  def update_active_for_method(self, method: Method) -> None:
    self._active = method == self._method
    self._subject.on_next(
        constraints.ConstraintChangeEvent(self, None, None, None, None))

  def is_modifiable(self, key: str) -> bool:
    del key
    if self._allow_inactive_modifications_semaphore:
      return True
    return self._active

  @contextlib.contextmanager
  def _allow_inactive_modifications(self) -> Iterator[None]:
    self._allow_inactive_modifications_semaphore += 1
    yield
    self._allow_inactive_modifications_semaphore -= 1


class IdentifyRegionsConstraints(constraints.Constraints):
  method: Method = Method.LINES_CLASSIFIER

  _method_constraint_map: Dict[Method, BaseRegionConstraints] = None

  def __init__(self) -> None:
    super().__init__()
    self._method_constraint_map = {}

  def register_method_constraint(
      self, constraint: BaseRegionConstraints) -> None:
    self._method_constraint_map[constraint.get_method()] = constraint
    constraint.update_active_for_method(self.method)

  def _before_change_event(
      self, event: constraints.ConstraintChangeEvent) -> None:
    if event.key != 'method':
      return
    with self._pause_events():
      for constraint in self._method_constraint_map.values():
        constraint.update_active_for_method(event.current)
