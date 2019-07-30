"""
A step may have dependencies and constraints.
"""

from typing import Iterable, Optional

from puzzle.constraints import constraints as constraints_module

Constraints = Iterable[constraints_module.Constraints]
Dependencies = Iterable['Step']

class Step(object):
  _constraints: Constraints
  _dependencies: Dependencies

  def __init__(
      self,
      dependencies: Optional[Dependencies] = None,
      constraints: Optional[Constraints] = None) -> None:
    if dependencies:
      self._dependencies = list(dependencies)
    else:
      self._dependencies = []
    if constraints:
      self._constraints = list(constraints)
    else:
      self._constraints = []

  def __len__(self) -> int:
    return 1 + sum(len(dep) for dep in self._dependencies)
