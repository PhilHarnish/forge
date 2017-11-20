from data.seek_sets import grid_seek_set
from spec.mamba import *

with description('grid_seek_set'):
  with description('construction'):
    with it('constructs with empty set'):
      expect(calling(grid_seek_set.GridSeekSet, [])).not_to(raise_error)

    with it('constructs with list of strings'):
      expect(calling(grid_seek_set.GridSeekSet, [
        'test',
        'test',
      ])).not_to(raise_error)

    with it('constructs with list of lists'):
      expect(calling(grid_seek_set.GridSeekSet, [
        ['t', 'es', 't'],
        ['t', 'es', 't'],
      ])).not_to(raise_error)

    with it('constructs with list with sets'):
      expect(calling(grid_seek_set.GridSeekSet, [
        ['t', 'es', 't'],
        ['t', set('es'), 't'],
      ])).not_to(raise_error)

  with description('SEARCH indexing'):
    with before.each:
      self.subject = grid_seek_set.GridSeekSet([
        ['a', 'b', 'c', 'd'],
        ['e', 'f', 'g', 'x'],
        ['i', 'j', 'k', 'l'],
        ['x', 'n123', set('ost'), 'p'],
      ])

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal(set('abcdefgxijklxnopst')))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal(set('bef')))

    with it('rejects invalid paths'):
      expect(self.subject['akp']).to(equal(set()))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['abc']).to(equal({'d'}))

    with it('supports indexing for diagnal multi-character query'):
      expect(self.subject['pkf']).to(equal({'a'}))

    with it('supports indexing into multi-character cells'):
      expect(self.subject['n12']).to(equal({'3'}))

    with it('supports indexing out of multi-character cells (into set)'):
      expect(self.subject['n123']).to(equal(set('ijkxost')))

    with it('supports indexing for ambiguous query'):
      expect(self.subject['x']).to(equal(set('cdgklijn')))

  with description('COLUMN indexing'):
    with before.each:
      self.subject = grid_seek_set.GridSeekSet([
        ['a', 'b', 'c', 'd'],
        ['e', 'f', 'g', 'x'],
        ['i', 'j123', 'k', 'l'],
        ['x', 'n', 'o', 'p'],
      ], mode=grid_seek_set.COLUMN)

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal(set('aeix')))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal(set('bfjn')))

    with it('rejects invalid paths'):
      expect(self.subject['akp']).to(equal(set()))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['abc']).to(equal(set('dxlp')))

    with it('supports indexing into multi-character cell'):
      expect(self.subject['aj12']).to(equal(set('3')))

    with it('supports indexing out of multi-character cell'):
      expect(self.subject['aj123']).to(equal(set('cgko')))

  with description('ROW indexing'):
    with before.each:
      self.subject = grid_seek_set.GridSeekSet([
        ['a', 'b', 'c', 'd'],
        ['e', 'f', 'g', 'x'],
        ['i', 'j123', 'k', 'l'],
        ['x', 'n', 'o', 'p'],
      ], mode=grid_seek_set.ROW)

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal(set('abcd')))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal(set('efgx')))

    with it('rejects invalid paths'):
      expect(self.subject['akp']).to(equal(set()))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['ae']).to(equal(set('ijkl')))

    with it('supports indexing into multi-character cell'):
      expect(self.subject['aej12']).to(equal(set('3')))

    with it('supports indexing out of multi-character cell'):
      expect(self.subject['aej123']).to(equal(set('xnop')))

  with description('KNIGHT indexing'):
    with before.each:
      self.subject = grid_seek_set.GridSeekSet([
        ['a', 'b', 'c', 'd'],
        ['e', 'f', 'g', 'x'],
        ['i', 'j123', 'k', 'l'],
        ['x', 'n', 'o', 'p'],
      ], mode=grid_seek_set.KNIGHT)

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal(set('abcdefgxijklxnop')))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal(set('jg')))

    with it('rejects invalid paths'):
      expect(self.subject['akp']).to(equal(set()))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['ag']).to(equal(set('ainp')))

    with it('supports indexing into multi-character cell'):
      expect(self.subject['aj12']).to(equal(set('3')))

    with it('supports indexing out of multi-character cell'):
      expect(self.subject['aj123']).to(equal(set('acpx')))

  with description('SNAKE indexing'):
    with before.each:
      self.subject = grid_seek_set.GridSeekSet([
        ['a', 'b', 'c', 'd'],
        ['e', 'f', 'g', 'x'],
        ['i', 'j123', 'k', 'l'],
        ['x', 'n', 'o', 'p'],
      ], mode=grid_seek_set.SNAKE)

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal(set('abcdefgxijklxnop')))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal(set('bef')))

    with it('rejects invalid paths'):
      expect(self.subject['akp']).to(equal(set()))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['ab']).to(equal(set('acefg')))

    with it('supports indexing into multi-character cell'):
      expect(self.subject['aej12']).to(equal(set('3')))

    with it('supports indexing out of multi-character cell'):
      expect(self.subject['aej123']).to(equal(set('efgikxno')))

  with description('COMPASS indexing'):
    with before.each:
      self.subject = grid_seek_set.GridSeekSet([
        ['a', 'b', 'c', 'd'],
        ['e', 'f', 'g', 'x'],
        ['i', 'j123', 'k', 'l'],
        ['x', 'n', 'o', 'p'],
      ], mode=grid_seek_set.COMPASS)

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal(set('abcdefgxijklxnop')))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal(set('be')))

    with it('rejects invalid paths'):
      expect(self.subject['abg']).to(equal(set()))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['ab']).to(equal(set('acf')))

    with it('supports indexing into multi-character cell'):
      expect(self.subject['ij12']).to(equal(set('3')))

    with it('supports indexing out of multi-character cell'):
      expect(self.subject['nj123']).to(equal(set('fikn')))

  with description('READING indexing'):
    with before.each:
      self.subject = grid_seek_set.GridSeekSet([
        ['a', 'b', 'c', 'd'],
        ['e', 'f', 'g', 'x'],
        ['i', 'j123', 'k', 'l'],
        ['x', 'n', 'o', 'p'],
      ], mode=grid_seek_set.READING)

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal(set('abcdefgxijklxnop')))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal(set('be')))

    with it('rejects invalid paths'):
      expect(self.subject['cba']).to(equal(set()))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['ab']).to(equal(set('c')))

    with it('supports indexing into multi-character cell'):
      expect(self.subject['ij12']).to(equal(set('3')))

    with it('supports indexing out of multi-character cell'):
      expect(self.subject['fj123']).to(equal(set('n')))
