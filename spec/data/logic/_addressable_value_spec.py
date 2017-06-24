from data.logic import _addressable_value
from spec.mamba import *

with description('_addressable_value.AddressableValue'):
  with it('exposes an interface'):
    addressable = _addressable_value.AddressableValue()
    expect(addressable).to(have_property('dimension_address'))
    expect(addressable).to(have_property('dimension_address_name'))
