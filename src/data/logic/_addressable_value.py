class AddressableValue(object):
  """Base class for addressable values.

  Resolves circular dependency.
  """

  def dimension_address(self):
    raise NotImplementedError()

  def dimension_address_name(self):
    raise NotImplementedError()
