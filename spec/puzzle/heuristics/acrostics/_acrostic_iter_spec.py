import collections

from mock.mock import patch

from data import warehouse, word_frequencies
from data.seek_sets import seek_set
from puzzle.heuristics.acrostics import _acrostic_iter
from puzzle.puzzlepedia import prod_config
from spec.data.fixtures import tries
from spec.mamba import *

BA_PREFIX_TRIE = word_frequencies.load(
    reversed(list(zip(
        ('bad', 'bag', 'ban', 'bar', 'bat'),
        range(10**9, 10**9 + 6)))))


with description('acrostic'):
  with description('basics'):
    with it('uses a mock trie'):
      a = _acrostic_iter.AcrosticIter(['is'])
      expect(len(a._trie)).to(be_below(100))

    with it('yields simple solutions'):
      a = _acrostic_iter.AcrosticIter('is')
      expect(list(a)).to(contain('is'))

    with it('is observable'):
      a = _acrostic_iter.AcrosticIter('is')
      subs = mock.Mock()
      a.subscribe(subs)
      expect(subs.on_next.call_args).to(equal(mock.call('is')))

    with it('yields multi-character solutions'):
      a = _acrostic_iter.AcrosticIter(list('bag'), trie=BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bag'))

    with it('yields unique solutions'):
      a = _acrostic_iter.AcrosticIter(list('ba') + ['ggg'], trie=BA_PREFIX_TRIE)
      expect(list(a)).to(have_len(1))

    with it('yields multiple multi-character solutions'):
      a = _acrostic_iter.AcrosticIter(list('ba') + ['dgnrt'], trie=BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bad', 'bag', 'ban', 'bar', 'bat'))

  with description('_iter_phrases'):
    with before.all:
      self.subject = _acrostic_iter.AcrosticIter(['a'])

    with it('yields nothing for empty input'):
      phrases = self.subject._iter_phrases({})
      expect(phrases).to(have_len(0))

    with it('yields all items from single dict'):
      input = [('first', 10), ('second', 9), ('third', 8), ('fourth', 7)]
      p = {
        1: collections.OrderedDict(input),
      }
      phrases = list(self.subject._iter_phrases(p))
      expect(phrases).to(have_len(4))
      expect(phrases).to(equal(input))

    with it('yields items from multiple dicts in sorted order'):
      input1 = [('a', 10), ('b', 9), ('c', 5), ('d', 4)]
      input2 = [('e', 25), ('f', 8), ('g', 3), ('h', 1)]
      input3 = [('i', 15), ('j', 7), ('k', 6), ('l', 2)]
      p = {
        1: collections.OrderedDict(input1),
        2: collections.OrderedDict(input2),
        3: collections.OrderedDict(input3),
      }
      phrases = list(self.subject._iter_phrases(p))
      expect(phrases).to(have_len(len(input1 + input2 + input3)))
      expect(phrases).to(equal(
          sorted(input1 + input2 + input3, key=lambda x: x[1], reverse=True)
      ))

    with it('is used to cache results from previous walks'):
      a = _acrostic_iter.AcrosticIter(list('ba') + ['dgnrt'], trie=BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bad', 'bag', 'ban', 'bar', 'bat'))
      expect(list(a._phrase_graph[0][3].items())).to(equal([
        ('bat', 1000000004), ('bar', 1000000003), ('ban', 1000000002),
        ('bag', 1000000001), ('bad', 1000000000),
      ]))

  with context('when given ambiguous input text'):
    with before.each:
      self.patch = patch.object(_acrostic_iter, '_TARGET_WORD_SCORE_RATE', 1)
      self.patch.start()

    with after.each:
      self.patch.stop()

    with it('finds multiple words'):
      a = _acrostic_iter.AcrosticIter(list('superbowl'), tries.ambiguous())
      expect(list(a)).to(contain('super bowl', 'superb owl', 'superbowl'))

    with it('finds multiple words in really long string'):
      text = 'superbowlwarplanesnapshotscrapbookisnowhere'
      a = _acrostic_iter.AcrosticIter(list(text), tries.ambiguous())
      expect(''.join(next(iter(a)).split())).to(equal(text))

    with it('finds same answer quickly'):
      text = 'superbowlwarplanesnapshotscrapbookisnowhere'
      a = _acrostic_iter.AcrosticIter(list(text), tries.ambiguous())
      first = next(iter(a))
      # Result should be cached and '_walk' should never be needed.
      with patch.object(a, '_walk', side_effect=[]) as mock:
        second = next(iter(a))
        expect(first).to(equal(second))
        expect(mock.call_count).to(be_below(10))

    with description('with seek sets'):
      with it('maintains old functionality'):
        seeking = seek_set.SeekSet(list('superbowl'))
        a = _acrostic_iter.AcrosticIter(seeking, tries.ambiguous())
        expect(list(a)).to(contain('super bowl', 'superb owl', 'superbowl'))

      with it('supports indexing'):
        seeking = seek_set.SeekSet(['bad', 'bag', 'ban'], indexes=[1, 2, 3])
        a = _acrostic_iter.AcrosticIter(seeking, trie=BA_PREFIX_TRIE)
        expect(list(a)).to(equal(['ban']))

      with it('supports ambiguous indexing'):
        seeking = seek_set.SeekSet(['bad', 'bag', 'dgn'], indexes=[1, 2, None])
        a = _acrostic_iter.AcrosticIter(seeking, trie=BA_PREFIX_TRIE)
        expect(list(a)).to(equal(['ban', 'bag', 'bad']))

      with it('supports permuted sets'):
        seeking = seek_set.SeekSet(
            ['dgn', 'aaa', 'bbb'],
            sets_permutable=True)
        a = _acrostic_iter.AcrosticIter(seeking, trie=BA_PREFIX_TRIE)
        expect(list(a)).to(equal(['ban', 'bag', 'bad']))

      with it('supports permuted sets (with indexes)'):
        seeking = seek_set.SeekSet(
            ['dgn', 'aaa', 'bbb'],
            sets_permutable=True,
            indexes=[1, 2, 3])
        a = _acrostic_iter.AcrosticIter(seeking, trie=BA_PREFIX_TRIE)
        expect(list(a)).to(equal(['ban']))

  with _description('real data'):
    with before.all:
      warehouse.save()
      prod_config.init()

    with after.all:
      prod_config.reset()
      warehouse.restore()

    with it('finds simple words'):
      a = _acrostic_iter.AcrosticIter('cab')
      expected = [
        'cab',
        'ca b',
        'c ab',
      ]
      for i, (answer, weight) in enumerate(a.items()):
        expect('#%s = %s @ %s' % (i, answer, weight)).to(equal(
            '#%s = %s @ %s' % (i, expected[i], weight)
        ))
      expect(a.items()).to(have_len(len(expected)))

    with it('finds important words'):
      a = _acrostic_iter.AcrosticIter('binary')
      expect(next(a.items())).to(equal(('binary', 1)))

    with _it('crazy expensive'):
      words = [
        'champion', 'nitpick', 'conspiracy', 'windpipe', 'epinephrine',
        'philanthropic', 'sierpinski', 'mississippi', 'pilaf', 'vulpine',
        'spinach', 'pinochet', 'porcupine', 'megapixels', 'australopithecus',
        'sharpie', 'intrepid', 'insipid', 'robespierre'
      ]
      a = _acrostic_iter.AcrosticIter(words)
      limit = 1000000
      for i, (answer, weight) in enumerate(a.items()):
        if answer.startswith('answer') or i % (limit / 10) == 0:
          print(answer, weight)
        if i > limit:
          print('tried %s' % i)
          break
      """ 4/24
      a to incipient each rss 120548796
      a to incipient opps eii 153396
      a to incipient eipe rni 59329
      a to incipient ipps epe 174519
      a to incipient cmss ede 290375
      a to incipient csts rsr 175192
      a to incipient opca dsr 752124
      a to incipient cisr tnp 87249
      a to incipient ilos dps 1290835
      a to pntemplates cs tio 770193
      a to perempuan usps tio 770193

      4/25 + early break in walk when scores are low
      a to incipient each rss 120548796
      a to incipient iste eie 57198
      a to incipient cmss dss 1995347
      a to incipient imia rsi 697477
      a to incipient osrs eip 398559
      a to perempuan peas tpe 275152
      a to perempuan imcs nss 990710
      a to perempuan caar ens 717319
      a to perempuan usea tns 523866
      a to perempuan epra pii 512601
      a to dicipline imps psi 6101411
      """
