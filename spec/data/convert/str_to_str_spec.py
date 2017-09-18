from data.convert import str_to_str
from spec.mamba import *

with description('str_to_str'):
  with before.each:
    self.convert = lambda s, m: list(str_to_str.str_to_str(s, m))

  with it('handles empty input'):
    expect(self.convert('', {})).to(equal(['']))

  with it('trivial conversion'):
    expect(self.convert('a', {'a': ['b']})).to(equal(['b']))

  with it('duplicate conversion'):
    expect(self.convert('a', {'a': ['b', 'c']})).to(equal(['b', 'c']))

  with it('complex conversion'):
    expect(self.convert('ab', {
      'a': ['b', 'c'],
      'b': ['d', 'e'],
      'ab': ['f'],
    })).to(equal(['bd', 'be', 'cd', 'ce', 'f']))
