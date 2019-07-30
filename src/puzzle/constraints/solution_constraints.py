from typing import List, Optional

from puzzle.constraints import constraints, validator

_THRESHOLD = 0.01


class SolutionConstraints(constraints.Constraints):
  solution_enumeration: Optional[List[int]] = None
  solution_length: Optional[validator.StrLenInRange(min_value=0)] = None
  solution_min_length: Optional[validator.StrLenInRange(min_value=0)] = None
  weight_threshold: validator.NumberInRange(
      min_value=0.0, max_value=1.0) = _THRESHOLD

  def has_enumeration(self, enumeration: List[int]) -> None:
    self.solution_enumeration = enumeration

  def is_solution_valid(self, solution: str, weight: float) -> bool:
    if weight < self.weight_threshold:
      return False
    solution_length = _str_len(solution)
    if self.solution_length and solution_length != self.solution_length:
      return False
    if self.solution_min_length and solution_length < self.solution_min_length:
      return False
    if (self.solution_enumeration and
        solution.count(' ') + 1 == len(self.solution_enumeration) and not all(
            _str_len(k) == l for k, l in zip(
                solution.split(' '), self.solution_enumeration))):
      return False
    return True


def _str_len(s: str) -> int:
  return sum(c.isalnum() for c in s)
