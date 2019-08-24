import enum
from typing import Dict

from puzzle.constraints import constraints


class Method(enum.Enum):
  LINES_CLASSIFIER = enum.auto()
  RECTANGULAR_GRID = enum.auto()
  HEXAGONAL_GRID = enum.auto()


class BaseRegionConstraints(constraints.Constraints):
  _method: Method = None
  _active: bool = False

  def get_method(self) -> Method:
    return self._method

  def update_active_for_method(self, method: Method) -> None:
    self._active = method == self._method
    self._subject.on_next(
        constraints.ConstraintChangeEvent(self, None, None, None))

  def is_modifiable(self, key: str) -> bool:
    del key
    return self._active


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
    for constraint in self._method_constraint_map.values():
      constraint.update_active_for_method(event.current)
