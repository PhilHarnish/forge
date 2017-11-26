from puzzle.stream import stream_manager
from spec.mamba import *


with description('constructor'):
  with it('constructs without error'):
    expect(calling(stream_manager.StreamManager)).not_to(raise_error)

with description('register_stream'):
  with before.each:
    self.subject = stream_manager.StreamManager()

  with it('invents name if not specified'):
    self.subject.register_stream(None, ['a', 'b', 'c'])
    expect(self.subject.get_streams()).to(equal({'_0': ['a', 'b', 'c']}))

  with it('increments name if needed'):
    self.subject.register_stream(None, ['a'])
    self.subject.register_stream(None, ['b'])
    expect(self.subject.get_streams()).to(equal({'_0': ['a'], '_1': ['b']}))

  with it('uses name if specified'):
    self.subject.register_stream('name', ['a', 'b', 'c'])
    expect(self.subject.get_streams()).to(equal({'name': ['a', 'b', 'c']}))
