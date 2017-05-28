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

    with description('indexing'):
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
        expect(self.subject['123']).to(contain('4'))
        expect(self.subject[['3', 'a', 'b']]).to(contain('d'))
        expect(self.subject[['3', 'a', 'b', 'c']]).to(be_empty)
