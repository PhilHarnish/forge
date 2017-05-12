from spec.mamba import *

from data import warehouse

with description('warehouse'):
  with after.each:
    warehouse.reset()

  with it('should register data'):
    warehouse.register('/some/path', 'some value')
    expect(call(warehouse.get, '/some/path')).to(equal('some value'))

  with it('should raise KeyError for unregistered data'):
    expect(calling(warehouse.get, '/some/path')).to(raise_error(KeyError))
