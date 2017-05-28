from data import seek_set
from spec.mamba import *

with description('seek_set'):
  with description('simple'):
    with description('construction'):
      with it('constructs with empty set'):
        expect(calling(seek_set.SeekSet, [])).not_to(raise_error)

      with it('constructs with string'):
        expect(calling(seek_set.SeekSet, 'example')).not_to(raise_error)

      with it('constructs with list of strings'):
        expect(calling(seek_set.SeekSet, ['a', 'bc', 'de'])).not_to(raise_error)

      with it('constructs with list-of-lists'):
        expect(calling(seek_set.SeekSet, [
          ['a'], ['b', 'c'], ['d', 'e', 'f']
        ])).not_to(raise_error)

    with description('indexing without indexes'):
      with before.each:
        self.subject = seek_set.SeekSet(['a', 'bc', 'def', 'hijk', 'lmnop'])

      with it('supports "contains" for simple query'):
        expect(self.subject['']).to(contain('a'))

      with it('supports "contains" for simple multi-character query'):
        expect(self.subject['a']).to(contain('b'))

      with it('supports "contains" for complex query'):
        expect(self.subject['abd']).to(contain('h'))
        expect(self.subject[['a', 'b', 'd']]).to(contain('h'))
        expect(self.subject[['a', 'b', 'd']]).to_not(contain('a'))

    with description('indexing with indexes'):
      with before.each:
        self.subject = seek_set.SeekSet(
            ['a', 'bc', 'def', 'hijk', 'lmnop'],
            indexes=[1, 2, 3, 4, 5],
        )

      with it('supports "contains" for simple query'):
        expect(self.subject['']).to(equal({'a'}))

      with it('supports "contains" for simple multi-character query'):
        expect(self.subject['a']).to(equal({'c'}))

      with it('supports "contains" for complex query'):
        expect(self.subject['acfk']).to(equal({'p'}))

      with it('rejects anything off of the path'):
        expect(self.subject['abcd']).to(be_empty)

    with description('indexing with missing indexes'):
      with before.each:
        self.subject = seek_set.SeekSet(
            ['a', 'bc', 'def', 'hijk', 'lmnop'],
            indexes=[1, 2, 3, None, 5],
        )

      with it('supports "contains" for simple query'):
        expect(self.subject['']).to(equal({'a'}))

      with it('supports "contains" for simple multi-character query'):
        expect(self.subject['a']).to(equal({'c'}))

      with it('supports "contains" for complex query'):
        expect(self.subject['acfh']).to(equal({'p'}))
        expect(self.subject['acfi']).to(equal({'p'}))
        expect(self.subject['acfj']).to(equal({'p'}))
        expect(self.subject['acfk']).to(equal({'p'}))

  with description('permutable sets'):
    with description('construction'):
      with it('constructs with empty set'):
        expect(
            calling(seek_set.SeekSet, [], sets_permutable=True)
        ).not_to(raise_error)

      with it('constructs with string'):
        expect(
            calling(seek_set.SeekSet, 'example', sets_permutable=True)
        ).not_to(raise_error)

      with it('constructs with list of strings'):
        expect(
            calling(seek_set.SeekSet, ['a', 'bc', 'de'], sets_permutable=True)
        ).not_to(raise_error)

    with description('simple, words of length 1'):
      with before.each:
        self.subject = seek_set.SeekSet(list('abcdefg'), sets_permutable=True)

      with it('rejects "contains" garbage input'):
        expect(self.subject['']).not_to(contain('q'))

      with it('supports "contains" for simple query'):
        expect(self.subject['']).to(contain('a'))

      with it('supports "contains" for single character query'):
        expect(self.subject['a']).to(contain('b'))

      with it('supports "contains" for complex query'):
        expect(self.subject['abd']).to(contain('e'))
        expect(self.subject[['a', 'b', 'c']]).to(contain('g'))
        expect(self.subject[['a', 'b', 'c']]).to_not(contain('a'))

    with description('complex, words of various lengths'):
      with before.each:
        self.subject = seek_set.SeekSet([
          '1a',
          '2ab',
          '3abc',
          '4abcd',
        ], sets_permutable=True)

      with it('rejects "contains" garbage input'):
        expect(self.subject['']).not_to(contain('q'))

      with it('supports "contains" for simple query'):
        expect(self.subject['']).to(contain('a'))

      with it('supports "contains" for single character query'):
        expect(self.subject['a']).to(contain('b'))

      with it('supports "contains" for complex query'):
        expect(self.subject['123']).to(equal(set('4abcd')))
        expect(self.subject[['b', 'b', 'b']]).to(equal(set('1a')))
        expect(self.subject[['3', 'a', 'b']]).to(equal(
            set('1a') | set('2ab') | set('4abcd')))
        expect(self.subject[['3', 'a', 'b', 'c']]).to(be_empty)

    with description('complex + indexes'):
      with before.each:
        self.subject = seek_set.SeekSet([
          '1a',
          '2ax',
          '3ayi',
          '4azjq',
        ], sets_permutable=True, indexes=[1, 2, 3, 4])

      with it('rejects "contains" garbage input'):
        expect(self.subject['']).not_to(contain('q'))

      with it('supports "contains" for simple query'):
        expect(self.subject['']).to(equal({'1', '2', '3', '4'}))

      with it('supports "contains" for single character query'):
        expect(self.subject['1']).to(equal({'a'}))

      with it('supports "contains" for complex query'):
        expect(self.subject['1a']).to(equal({'x', 'y', 'z'}))
        expect(self.subject['1ax']).to(equal({'i', 'j'}))
        expect(self.subject['1ay']).to(equal({'j'}))

      with it('recognizes index > set length'):
        self.subject = seek_set.SeekSet([
          'a5',
          'b2345',
          'd2345',
        ], sets_permutable=True, indexes=[5, 5, 1])
        expect(self.subject['']).to(equal({'5'}))
        expect(self.subject['5']).to(equal({'5'}))
        expect(self.subject['55']).to(equal({'a'}))
