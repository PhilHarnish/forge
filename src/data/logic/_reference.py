from data import operator_overloading
from data.logic import _util


_UNDEFINED = {}


def _make_operator(op, _):
  return lambda self, other: op(coerce_value(self), coerce_value(other))


@operator_overloading.overload_with_fn(_make_operator)
class ValueReference(operator_overloading.OverloadedSelfBase):
  def __init__(self, model, value):
    self._model = model
    self._value = value

  def value(self):
    if self._value is not _UNDEFINED:
      return self._value
    raise TypeError('%s does not have a value' % self)

  def __str__(self):
    return str(self.value())


class Reference(ValueReference):
  """Holds a reference to a dimension Name."""

  def __init__(self, model, constraints):
    if len(constraints) == 1:
      value = next(iter(constraints.values()))
    else:
      value = _UNDEFINED
    super(Reference, self).__init__(model, value)
    self._constraints = constraints

  def __eq__(self, other):
    """Merge constraints."""
    if isinstance(other, Reference):
      try:
        return Reference(
            self._model,
            _util.combine(self._constraints, other._constraints))
      except KeyError:
        # If self and other are both constrained on similar dimensions then
        # combining them is impossible and ordinary equality should be used.
        pass
    return super(Reference, self).__eq__(other)

  def __ne__(self, other):
    """Merge constraints."""
    if isinstance(other, Reference):
      return Reference(
          self._model,
          _util.combine(self._constraints, other._constraints)) == False
    return super(Reference, self).__ne__(other)

  def __lshift__(self, other):
    pass

  def __rshift__(self, other):
    pass

  def value(self):
    # If the Reference is under-constrained there won't be any matching
    # variables. However, an unconstrained Reference may have one constraint
    # value which could be returned instead.
    return (self._model.get_variables(self._constraints) or
            super(Reference, self).value())

  @property
  def ident(self):
    raise TypeError('Attempted to model a Reference object (%s)' % self)


def coerce_value(value):
  if isinstance(value, ValueReference):
    return value.value()
  return value
