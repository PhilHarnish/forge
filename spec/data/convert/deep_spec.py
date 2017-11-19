from data.convert import deep
from spec.mamba import *

with description('deep'):
  with it('handles empty input'):
    expect(deep.lower('')).to(equal(''))

  with it('trivial conversion'):
    expect(deep.lower('AsDf')).to(equal('asdf'))

  with it('list conversion'):
    expect(deep.lower(['AsDf', 'QWERTY'])).to(equal(['asdf', 'qwerty']))

  with it('tuple conversion'):
    expect(deep.lower(('AsDf', 'QWERTY'))).to(equal(('asdf', 'qwerty')))

  with it('set conversion'):
    expect(deep.lower({'AsDf', 'QWERTY'})).to(equal({'asdf', 'qwerty'}))

  with it('dict conversion'):
    expect(deep.lower({
      'FIRST':'AsDf',
      'SECOND': 'QWERTY',
    })).to(equal({'first': 'asdf', 'second': 'qwerty'}))

  with it('mixed conversion'):
    expect(deep.lower({
      'FIRST': ['1', '2', 'ASDF'],
      'SECOND': 'QWERTY',
      'THIRD': {'X', 'Y', 'Z'},
    })).to(equal({
      'first': ['1', '2', 'asdf'],
      'second': 'qwerty',
      'third': {'y', 'x', 'z'},
    }))
