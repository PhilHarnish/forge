"""Base class for a value with an address and constraints."""


class AddressableValue(object):
  """Base class for addressable values.

  Resolves circular dependency.
  """

  def dimension_constraints(self):
    """:returns dict representation of constraints."""
    raise NotImplementedError()

  def dimension_address(self):
    """:returns str representation of constraints."""
    raise NotImplementedError()
