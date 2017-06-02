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
        expect(subject['']).to(contain(*'abcdefghijklmnopqrstuvwxyz'))

      with it('rejects impossibly long seeks'):
        bomb = crypto_seek_set.CryptoSeekSet('a')
        expect(lambda: bomb['aaa']).to(raise_error(IndexError))

      with it('supports "contains" for simple multi-character query'):
        subject = crypto_seek_set.CryptoSeekSet('xyz')
        expect(subject['a']).to(contain(*'bcdefghijklmnopqrstuvwxyz'))

      with it('returns empty set when matches line up'):
        subject = crypto_seek_set.CryptoSeekSet('xyz')
        expect(subject['abc']).to(be_empty)

      with it('supports "contains" for complex query'):
        subject = crypto_seek_set.CryptoSeekSet('abcdefghijklmnopqrstuvwxyz')
        expect(subject['bcdefghijklmnopqrstuvwxyz']).to(equal({'a'}))
