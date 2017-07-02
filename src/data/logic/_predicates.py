import Numberjack

# Try to de-prioritize any Numberjack primitives so that our operators
# take precedence.
_LOWER_PRIORITY = (
  Numberjack.Predicate,
)


class Predicates(list):
  def __init__(self, values):
    super(Predicates, self).__init__(values)

  def _zip(self, other):
    for child in self:
      if isinstance(child, _LOWER_PRIORITY):
        yield other, child
      else:
        yield child, other

  def __eq__(self, other):
    return Predicates([left == right for left, right in self._zip(other)])

  def __ne__(self, other):
    return Predicates([left != right for left, right in self._zip(other)])

  def __add__(self, other):
    return Predicates([left + right for left, right in self._zip(other)])

  def __sub__(self, other):
    return Predicates([child - other for child in self])

  def __lt__(self, other):
    return Predicates([child < other for child in self])

  def __le__(self, other):
    return Predicates([child <= other for child in self])

  def __gt__(self, other):
    return Predicates([child > other for child in self])

  def __ge__(self, other):
    return Predicates([child >= other for child in self])

  def __or__(self, other):
    # TODO: This should really be a cross product.
    return Predicates([left | right for left, right in self._zip(other)])

  def __xor__(self, other):
    # TODO: This should really be a cross product.
    # This shortcut may not always work. When does it fail?
    return Predicates([left + right == 1 for left, right in self._zip(other)])

  def __str__(self):
    return '\n'.join(map(str, self))
