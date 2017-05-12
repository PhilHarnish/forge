from mock.mock import patch

from spec.mamba import *

from data import warehouse

with description('warehouse'):
  with before.all:
    self.warehouse_patch = patch.object(warehouse, '_DATA', {})
    self.warehouse_patch.start()

  with after.all:
    self.warehouse_patch.stop()

  with before.each:
    warehouse.init()

  with after.each:
    warehouse.reset()

  with it('protects against non-hermetic tests'):
    expect(calling(warehouse.init)).to(raise_error)

  with it('protects against redundant registration'):
    expect(calling(warehouse.register, '/some/path', 1)).not_to(raise_error)
    expect(calling(warehouse.register, '/some/path', 1)).to(raise_error)

  with description('simple data'):
    with it('should register data'):
      warehouse.register('/some/path', 'some value')
      expect(call(warehouse.get, '/some/path')).to(equal('some value'))

    with it('should raise KeyError for unregistered data'):
      expect(calling(warehouse.get, '/some/path')).to(raise_error(KeyError))

  with description('constructed data'):
    with before.each:
      self.value = {'key': 'value'}
      self.source = lambda: self.value

    with it('should register data'):
      warehouse.register('/some/path', self.source)
      expect(call(warehouse.get, '/some/path')).to(equal(self.value))