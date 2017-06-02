from data.seek_sets import crypto_seek_set
from spec.mamba import *

with description('crypto_seek_set'):
  with description('simple'):
    with description('construction'):
      with it('constructs with empty str'):
        expect(calling(crypto_seek_set.CryptoSeekSet, '')).not_to(raise_error)

      with it('constructs with string'):
        expect(calling(crypto_seek_set.CryptoSeekSet, 'example')).not_to(
            raise_error)

      with it('cannot construct with list of strings'):
        expect(calling(crypto_seek_set.CryptoSeekSet, ['a', 'bc', 'de'])).to(
            raise_error)

      with it('cannot construct with list-of-lists'):
        expect(calling(crypto_seek_set.CryptoSeekSet, [
          ['a'], ['b', 'c'], ['d', 'e', 'f']
        ])).to(raise_error)

    with description('indexing'):
      with it('supports "contains" for simple query'):
        subject = crypto_seek_set.CryptoSeekSet('aaaaaa')
        expect(subject['']).to(equal(set('abcdefghijklmnopqrstuvwxyz')))

      with it('rejects impossibly long seeks'):
        bomb = crypto_seek_set.CryptoSeekSet('a')
        expect(lambda: bomb['aaa']).to(raise_error(IndexError))

      with it('supports "contains" for simple multi-character query'):
        subject = crypto_seek_set.CryptoSeekSet('xyz')
        expect(subject['a']).to(equal(set('bcdefghijklmnopqrstuvwxyz')))

      with it('returns empty set when matches line up'):
        subject = crypto_seek_set.CryptoSeekSet('xyz')
        expect(subject['abc']).to(be_empty)

      with it('supports "contains" for complex query'):
        subject = crypto_seek_set.CryptoSeekSet('abcdefghijklmnopqrstuvwxyz')
        expect(subject['bcdefghijklmnopqrstuvwxyz']).to(equal({'a'}))

      with it('recognizes when characters return'):
        subject = crypto_seek_set.CryptoSeekSet('ababab')
        # Imply a = x; return all unassigned letters since b is unknown.
        expect(subject['x']).to(equal(set('abcdefghijklmnopqrstuvwyz')))
        # Imply a = x, b = y; return x since a is known.
        expect(subject['xy']).to(equal(set('x')))
