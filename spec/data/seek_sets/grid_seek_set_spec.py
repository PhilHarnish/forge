from data.seek_sets import grid_seek_set
from spec.mamba import *

with description('grid_seek_set'):
  with description('construction'):
    with it('constructs with empty set'):
      expect(calling(grid_seek_set.GridSeekSet, [])).not_to(raise_error)

    with it('constructs with array of strings'):
      expect(calling(grid_seek_set.GridSeekSet, [
        'test',
        'test',
      ])).not_to(raise_error)

  with description('SEARCH indexing'):
    with before.each:
      self.subject = grid_seek_set.GridSeekSet([
        'abcd',
        'efgh',
        'ijkl',
        'mnop',
      ])

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal(set('abcdefghijklmnop')))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal(set('bef')))

    with it('rejects invalid paths'):
      expect(self.subject['akp']).to(equal(set()))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['abc']).to(equal({'d'}))

    with it('supports indexing for diagnal multi-character query'):
      expect(self.subject['pkf']).to(equal({'a'}))
