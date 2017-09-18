from data import warehouse
from data.seek_sets import chain_seek_set
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with description('seek_set'):
  with description('construction'):
    with it('constructs with empty set'):
      expect(calling(chain_seek_set.ChainSeekSet, [], 0)).not_to(raise_error)

    with it('constructs with list of strings'):
      expect(calling(chain_seek_set.ChainSeekSet, ['a', 'bc', 'de'], 1)).not_to(
          raise_error)

    with it('validates length'):
      expect(calling(chain_seek_set.ChainSeekSet, ['a', 'bc', 'de'], 9)).to(
          raise_error)

    with it('allows duplicate sets'):
      expect(calling(chain_seek_set.ChainSeekSet, ['ab', 'ab'], 1)).not_to(
          raise_error)

  with description('simple indexing'):
    with before.each:
      self.subject = chain_seek_set.ChainSeekSet(
          ['a', 'bc', 'def', 'hijk', 'lmnop'], 6)

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal({'a', 'b', 'd', 'h', 'l'}))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal({'b', 'd', 'h', 'l'}))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['abc']).to(equal({'d', 'h', 'l'}))

    with it('supports indexing partial match query'):
      expect(self.subject['hi']).to(equal({'j'}))

  with description('ambiguous indexing'):
    with before.each:
      self.subject = chain_seek_set.ChainSeekSet(
          ['a', 'ab1', 'ac2', 'ad3', 'aef4'], 6)

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal({'a'}))

    with it('supports indexing for simple single-character query'):
      expect(self.subject['a']).to(equal({'a', 'b', 'c', 'd', 'e'}))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['aab1']).to(equal({'a'}))

    with it('supports indexing partial match query'):
      expect(self.subject['aef']).to(equal({'4'}))

  with description('chained indexing'):
    with before.each:
      self.subject = chain_seek_set.ChainSeekSet(
          ['a', 'ab1', 'ac2', 'ad3', 'aef4'], 6)['a':]

    with it('supports indexing for simple query'):
      expect(self.subject['']).to(equal({'a', 'b', 'c', 'd', 'e'}))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['b1a']).to(equal({'a', 'e', 'c', 'd'}))

    with it('supports indexing partial match query'):
      expect(self.subject['aef']).to(equal({'4'}))

    with it('supports chaining indexes'):
      seek_set = self.subject['aef':]
      expect(seek_set['']).to(equal({'4'}))

  with description('indexing with prefix'):
    with before.each:
      self.subject = chain_seek_set.ChainSeekSet(
          ['a', 'ab1', 'ac2', 'ad3', 'aef4'], 6, prefix='a')

    with it('supports indexing for simple query'):
      expect(set(self.subject[''])).to(equal({'a'}))

    with it('supports indexing for simple multi-character query'):
      expect(self.subject['a']).to(equal({'a', 'b', 'c', 'd', 'e'}))

    with it('supports indexing partial match query'):
      expect(self.subject['aef']).to(equal({'4'}))

    with it('supports chaining indexes'):
      seek_set = self.subject['aef':]
      expect(seek_set['']).to(equal({'4'}))

_SETS = [
  're', 'n', 'se', 'ti', 'an', 'do', 'en', 'ic', 'il', 'me', 'se', 'si', 'tl',
  'sc', 'ty', 'on', 'th', 'e', 'es', 'rs', 'ad', 'da', 'ou', 'th', 'un', 'ck',
  'se', 'to', 'dom', 'eit', 'ly', 'ph', 'ra', 'ur', 'el', 'fr', 'pa', 'us',
  'ig', 'ee', 'el', 'ke', 'nt', 'yo', 'ia', 'in', 'at', 'it', 'yt', 'fl', 'lf',
  'rd', 'ha', 'yk', 'he', 'wa', 'ot', 'di', 'ht', 'io', 'ov', 's', 'ts', 've',
  'wo'
]

with description('real world test'):
  with before.all:
    warehouse.save()
    prod_config.init()
    self.trie = warehouse.get('/words/unigram/trie')

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('loads seek set'):
    expect(calling(chain_seek_set.ChainSeekSet, _SETS, 4)).not_to(raise_error)

  with it('finds results of length 2'):
    seek_set = chain_seek_set.ChainSeekSet(_SETS, 2)
    results = set()
    for result, weight in self.trie.walk(seek_set, exact_match=True):
      if weight < 5e8:
        break
      results.add(result)
    expect(results).to(equal({
      'in', 'on', 'it', 'at', 'us', 'do', 'no', 'he', 'so', 'me', 'to',
    }))

  with it('finds results of length 4'):
    seek_set = chain_seek_set.ChainSeekSet(_SETS, 4)
    results = set()
    for result, weight in self.trie.walk(seek_set, exact_match=True):
      if weight < 5e8:
        break
      results.add(result)
    expect(results).to(equal({
      'that', 'your', 'have', 'free', 'time', 'they', 'site', 'only', 'here',
      'than',
    }))

  with _it('finds results of length 4, 4, starting from on'):
    seek_set = chain_seek_set.ChainSeekSet(_SETS, 8, prefix='on')
    results = set()
    acc = []
    def walk(seek_set, acc, targets, pos=0):
      if pos >= len(targets):
        results.add(' '.join(acc))
        return
      target = targets[pos]
      seek_set.set_length(target)
      for result, weight in self.trie.walk(seek_set, exact_match=True):
        if weight < 5e8:
          break
        acc.append(result)
        walk(seek_set[result:], acc, targets, pos+1)
        acc.pop()
    walk(seek_set, acc, [4, 4])
    expect(results).to(equal({
      'only site', 'only that', 'only they', 'only than', 'only here',
      'only have', 'only your', 'only free', 'only time'
    }))

  with it('finds results of length 1, 6, 4, 12, starting from al'):
    seek_set = chain_seek_set.ChainSeekSet(_SETS, 8, prefix='al')
    results = set()
    acc = []
    def walk(seek_set, acc, targets, pos=0):
      if pos >= len(targets):
        results.add(' '.join(acc))
        return
      target = targets[pos]
      seek_set.set_length(target)
      for result, weight in self.trie.walk(seek_set, exact_match=True):
        if weight < 5e8:
          break
        acc.append(result)
        walk(seek_set[result:], acc, targets, pos+1)
        acc.pop()
    walk(seek_set, acc, [1, 6, 4, 12])
    expect(results).to(equal({
      'only site', 'only that', 'only they', 'only than', 'only here',
      'only have', 'only your', 'only free', 'only time'
    }))
