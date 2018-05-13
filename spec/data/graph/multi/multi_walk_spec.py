from data.graph import regex
from data.graph.multi import multi_walk
from spec.mamba import *

with description('multi_walk'):
  with it('accepts empty list'):
    expect(list(multi_walk.walk([]))).to(have_len(0))

  with it('accepts empty dict'):
    expect(list(multi_walk.walk({}))).to(have_len(0))

  with it('accepts fixed results'):
    expect(list(multi_walk.walk([
      regex.parse('foo'), regex.parse('bar'),
    ]))).to(equal([multi_walk.ResultSet([('foo', 1), ('bar', 1)])]))
