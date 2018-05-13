from typing import Optional


class State(dict):
  _hash = None

  def __eq__(self, other: 'State') -> bool:
    if self is other:
      return True
    return self.__dict__ == other.__dict__

  def __and__(self, other: 'State') -> Optional['State']:
    # Prefer constraints in "b".
    if other:
      a, b = self, other
    elif self:
      a, b = other, self
    else:
      return BLANK
    if not a:
      return b
    # Both a and b have constraints.
    if len(a) > len(b):
      b, a = a, b  # Prefer longer constraints in b.
    # First, verify equality among shared keys.
    if not all(a[k] == b[k] for k in a if k in b):
      return None
    combined_constraints = b.copy()
    combined_constraints.update(a)
    return State(combined_constraints)

  def __hash__(self) -> int:
    if self._hash is None:
      self._hash = hash(tuple(sorted(self.items(), key=lambda x: x[0])))
    return self._hash

BLANK = State()
