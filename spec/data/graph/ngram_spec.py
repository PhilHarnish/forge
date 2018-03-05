from data import pickle_cache
from data.graph import ngram
from spec.mamba import *

_1GRAM = """
the 1000000
a    750000
and  500000
for   25000
was   20000
are   18000
not   15000
of    14000
his   13000
had   10000
only   5000
next   4000
new    3000
been   2000
one    1000
man     500
"""
_2GRAM = """
and the 750000
for the 700000
was the 475000
his was 470000
but the 470000
and his 440000
are not 430000
are the 425000
you are 425000
not the 420000 
"""
_3GRAM = """
and the only 440000
for the next 438000
was not a    437000
was the only 437000
and for the  436000
for the new  435000
was not the  435000
had not been 435000
not the only 435000
and the new  434000
was the one  434000
and for a    433000
are not the  433000
and had a    433000
not for the  433000
and not the  432000
and not a    431000
and the man  431000
"""
_4GRAM = """
the end of the   440000
at the end of    430000
is one of the    430000
was one of the   430000
was the one who  425000
was the only one 425000
for the good of  424000
and the end of   423000
and the only way 423000
was not the only 423000
was not in the   422000
"""
_5GRAM = """
for the rest of the  390000
and the rest of the  390000
was the only one who 390000
and the end of the   390000
not the end of the   390000
was the end of the   390000
was the only way to  390000
not the only one who 390000
and for all of us    390000
was the one who had  392000
for the end of the   392000
and was one of the   392000
was the one who was  391000
for the sake of argument 391000
"""

def normalize(s: str) -> str:
  s = s.strip()
  return '\n'.join(' '.join(line.split()) for line in s.split('\n'))

_FILES = {
  'data/g1m_1gram.txt': normalize(_1GRAM),
  'data/coca_2gram.txt': normalize(_2GRAM),
  'data/coca_3gram.txt': normalize(_3GRAM),
  'data/coca_4gram.txt': normalize(_4GRAM),
  'data/coca_5gram.txt': normalize(_5GRAM),
}

def open_project_path_stub(f: str) -> Iterable[str]:
  return _FILES[f].split('\n')

open_project_path = mock.patch('data.graph.ngram.data.open_project_path')

with description('indexing') as self:
  with before.each:
    self.open_project_path = open_project_path.start()
    self.open_project_path.side_effect = open_project_path_stub
    pickle_cache.disable(('data/graph/ngram/index',))

  with after.each:
    open_project_path.stop()
    pickle_cache.enable(('data/graph/ngram/index',))

  with it('returns index for unigrams'):
    result = ngram.index('data/g1m_1gram.txt')
    expect(result).to(be_a(dict))
    expect(result['a']).to(equal([
      [('a', 750000, ('a', 1, None))],
      [],
      [
        ('and', 500000, ('a', 8201, ('n', 8200, ('d', 8, None)))),
        ('are', 18000, ('a', 131089, ('r', 131088, ('e', 16, None)))),
      ]
    ]))

  with it('returns index for other unigrams'):
    for f in _FILES:
      expect(call(ngram.index, f)).to(be_a(dict))


with description('get'):
  with before.each:
    self.open_project_path = open_project_path.start()
    self.open_project_path.side_effect = open_project_path_stub
    pickle_cache.disable((
      'data/graph/ngram/graph',
      'data/graph/ngram/index',
    ))

  with after.each:
    open_project_path.stop()
    pickle_cache.enable((
      'data/graph/ngram/graph',
      'data/graph/ngram/index',
    ))

  with it('returns a bloom node'):
    node = ngram.get()
    expect(repr(node)).to(equal("BloomNode('abdefhilmnorstwxy; ', ' ####', 0)"))

  with it('expands results'):
    node = ngram.get()
    expect(path_values(node, 'the')).to(look_like("""
      BloomNode('abdefhilmnorstwxy; ', ' ####', 0)
      t = BloomNode('EH; ', '  #', 0)
      h = BloomNode('E; ', ' #', 0)
      e = BloomNode('', '#', 1000000)
    """))
