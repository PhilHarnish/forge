from puzzle.pdql import q
from spec.mamba import *


with description('constructor'):
  with it('constructs without error'):
    expect(calling(q.Q)).not_to(raise_error)

with description('input'):
  with before.each:
    self.subject = q.Q()

  with it('accepts positional arguments'):
    self.subject.input('a', 'b', 'c')
    expect(self.subject.get_streams()).to(equal({'_0': ['a', 'b', 'c']}))

  with it('accepts multiple positional arguments'):
    self.subject.input(['a', 'b'], ['c'])
    expect(self.subject.get_streams()).to(equal({
      '_0': ['a', 'b'],
      '_1': ['c'],
    }))

  with it('accepts positional grid arguments'):
    self.subject.input([['a', 'b'], ['c', 'd']])
    expect(self.subject.get_streams()).to(equal({
      '_0': [['a', 'b'], ['c', 'd']]
    }))

  with it('accepts named arguments'):
    self.subject.input(grid=[['a', 'b'], ['c', 'd']])
    expect(self.subject.get_streams()).to(equal({
      'grid': [['a', 'b'], ['c', 'd']]
    }))
