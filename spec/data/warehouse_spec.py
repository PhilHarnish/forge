from spec.mamba import *

from data import warehouse

with description('warehouse'):
  with before.each:
    warehouse.init()

  with after.each:
    warehouse.reset()

  with it('should register data'):
    warehouse.register('/some/path', 'some value')
    expect(call(warehouse.get, '/some/path')).to(equal('some value'))

  with it('should raise KeyError for unregistered data'):
    expect(calling(warehouse.get, '/some/path')).to(raise_error(KeyError))

  with it('protects against non-hermetic tests'):
    expect(calling(warehouse.init)).to(raise_error)
