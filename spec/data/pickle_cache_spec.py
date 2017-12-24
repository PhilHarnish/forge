import os

from mock.mock import patch

from data import pickle_cache
from spec.mamba import *

pickle_patch = patch('data.pickle_cache.pickle')
pickle_path_patch = patch.object(pickle_cache, '_PICKLE_PATH', 'patched')
open_patch = patch.object(pickle_cache, '_open_pkl_path')
os_patch = patch('data.pickle_cache.os')

with description('pickle_cache'):
  with before.each:
    self.patched_pickle = pickle_patch.start()
    pickle_path_patch.start()
    self.patched_open = open_patch.start()
    original_join = os.path.join
    original_dirname = os.path.dirname
    self.patched_os = os_patch.start()
    self.patched_os.path.join.side_effect = original_join
    self.patched_os.path.dirname.side_effect = original_dirname

  with after.each:
    pickle_patch.stop()
    pickle_path_patch.stop()
    open_patch.stop()
    os_patch.stop()
    self.patched_os.stop()

  with description('_sanitize'):
    with it('sanitizes empty input'):
      expect(pickle_cache._sanitize('')).to(equal('_empty_str'))

    with it('sanitizes bool'):
      expect(pickle_cache._sanitize(True)).to(equal('True'))
      expect(pickle_cache._sanitize(False)).to(equal('False'))

    with it('sanitizes hazardous text'):
      expect(pickle_cache._sanitize('../../../')).to(equal('_306eec36b'))

    with it('sanitizes hazardous text uniquely'):
      expect(pickle_cache._sanitize('../../../')).not_to(equal(
          pickle_cache._sanitize('../../../../')))

  with description('_path_for_prefix_and_args'):
    with it('runs on empty input'):
      expect(pickle_cache._path_for_prefix_and_args('pre', [], {})).to(equal(
          'patched/pre/_.pkl'
      ))

    with it('runs for simple input'):
      expect(pickle_cache._path_for_prefix_and_args(
          'pre', ['a1', 'a2'], {'zzz': 'z', 'aaa': 'a', 'ccc': 'c'})).to(equal(
          'patched/pre/a1,a2/aaa-a,ccc-c,zzz-z.pkl'
      ))

  with description('cache'):
    with before.all:
      @pickle_cache.cache('prefix')
      def fn(*args, **kwargs):
        return args, kwargs


      self.fn = fn

    with it('creates a directory if none present'):
      self.patched_os.path.exists.return_value = False
      self.fn()
      expect(self.patched_os.makedirs).to(have_been_called_with(
          'patched/prefix', exist_ok=True))

    with it('loads pkl if present'):
      self.patched_os.path.exists.return_value = True
      self.patched_open.return_value = '<opened pkl>'
      self.fn()
      expect(self.patched_open).to(have_been_called_with(
          'patched/prefix/_.pkl', 'rb'))
      expect(self.patched_pickle.load).to(have_been_called_with('<opened pkl>'))

    with it('creates pkl if not present'):
      self.patched_os.path.exists.return_value = False
      self.patched_open.return_value = '<opened pkl>'
      self.fn(1, key='value')
      expect(self.patched_open).to(have_been_called_with(
          'patched/prefix/1/key-value.pkl', 'wb'))
      expect(self.patched_pickle.dump).to(have_been_called_with(
          ((1,), {'key': 'value'}), '<opened pkl>'))

  with description('cache_from_file'):
    with before.each:
      self.pkl_time = 0
      self.src_time = 0
      def stub_getmtime(path):
        if path.endswith('.pkl'):
          return self.pkl_time
        return self.src_time


      self.patched_os.path.getmtime.side_effect = stub_getmtime

      @pickle_cache.cache_from_file('prefix')
      def fn(path):
        return path


      self.fn = fn

    with it('ignores pkl if src is newer'):
      self.pkl_time = 0
      self.src_time = 20170101
      self.fn('file.py')
      expect(self.patched_pickle.load).not_to(have_been_called)

    with it('uses pkl if pkl is newer than src'):
      self.pkl_time = 201701010
      self.src_time = 0
      self.fn('file.py')
      expect(self.patched_pickle.load).to(have_been_called)
