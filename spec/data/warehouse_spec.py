import os
import pickle

from mock.mock import patch

from data import warehouse
from spec.mamba import *

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

  with description('save and restore'):
    with it('should clear the state when saved'):
      warehouse.register('/some/path', 1)
      warehouse.save()
      expect(calling(warehouse.get, '/some/path')).to(raise_error(KeyError))

    with it('should allow new changes'):
      warehouse.save()
      warehouse.register('/some/path', 2)
      expect(calling(warehouse.get, '/some/path')).not_to(raise_error(KeyError))

    with it('should allow restore old values'):
      warehouse.register('/some/path', 1)
      warehouse.save()
      warehouse.register('/some/path', 2)
      expect(call(warehouse.get, '/some/path')).to(equal(2))
      warehouse.restore()
      expect(call(warehouse.get, '/some/path')).to(equal(1))

  with description('pickle cache'):
    with before.each:
      self.getter = mock.Mock(return_value={'key': 'value'})
      self.pickle_dump = patch.object(pickle, 'dump', mock.Mock())
      self.pickle_dump_stub = self.pickle_dump.start()
      self.pickle_load = patch.object(pickle, 'load', return_value={
        'key': 'from pkl'
      })
      self.pickle_load_stub = self.pickle_load.start()
      self.path_exists = patch.object(os.path, 'exists', return_value=False)
      self.path_exists_stub = self.path_exists.start()
      self.warehouse_open = patch.object(
          warehouse, 'open', side_effect=lambda path, *args: path)
      self.warehouse_open.start()

    with after.each:
      self.pickle_dump.stop()
      self.pickle_load.stop()
      self.path_exists.stop()
      self.warehouse_open.stop()

    with it('should allow registering with a pickle cache'):
      expect(calling(warehouse.register, 'path', self.getter, True)).not_to(
          raise_error)

    with it('should look for pkl files in data/ dir'):
      warehouse.register('path', self.getter, True)
      expect(call(warehouse.get, 'path')).to(equal({'key': 'value'}))
      expect(self.path_exists_stub.call_args[0][0]).to(
          end_with('/data/path.pkl'))

    with it('should call getter and save if no pkl is present'):
      warehouse.register('path', self.getter, True)
      expect(call(warehouse.get, 'path')).to(equal({'key': 'value'}))
      expect(self.getter).to(have_been_called)
      expect(self.pickle_dump_stub).to(have_been_called)
      expect(self.pickle_dump_stub.call_args[0][1]).to(
          end_with('/data/path.pkl'))

    with it('should use pkl if present'):
      warehouse.register('path', self.getter, True)
      self.path_exists_stub.return_value = True
      expect(call(warehouse.get, 'path')).to(equal({'key': 'from pkl'}))
      expect(self.getter).not_to(have_been_called)
      expect(self.pickle_load_stub).to(have_been_called)
