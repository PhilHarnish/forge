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


class Reference(ValueReference):
  """Holds a reference to a dimension Name."""

  def __init__(self, model, constraints):
    super(Reference, self).__init__(model, _UNDEFINED)
    self._constraints = constraints

  def __eq__(self, other):
    """Merge constraints."""
    if isinstance(other, Reference):
      return Reference(
          self._model,
          _util.combine(self._constraints, other._constraints))
    return super(Reference, self).__eq__(other)

  def __ne__(self, other):
    """Merge constraints."""
    if isinstance(other, Reference):
      return Reference(
          self._model,
          _util.combine(self._constraints, other._constraints)) == False
    return super(Reference, self).__ne__(other)

  def value(self):
    return self._model._get_variables(self._constraints)


def coerce_value(value):
  if isinstance(value, ValueReference):
    return value.value()
  return value
