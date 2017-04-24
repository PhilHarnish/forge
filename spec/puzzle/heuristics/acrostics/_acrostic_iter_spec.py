import collections

import mock
from mock.mock import patch

from spec.mamba import *
from spec.data.fixtures import tries
from puzzle.heuristics.acrostics import _acrostic_iter
from data import word_frequencies

BA_PREFIX_TRIE = word_frequencies.load(
    zip(('bad', 'bag', 'ban', 'bar', 'bat'), range(1, 6)))


with description('acrostic'):
  with description('basics'):
    with it('uses a mock trie'):
      a = _acrostic_iter.Acrostic(['a'], tries.letters())
      expect(len(a._trie)).to(be_below(100))

    with it('yields simple solutions'):
      a = _acrostic_iter.Acrostic(['a'], tries.letters())
      expect(list(a)).to(contain('a'))

    with it('is observable'):
      a = _acrostic_iter.Acrostic(['a'], tries.letters())
      subs = mock.Mock()
      a.subscribe(subs)
      expect(subs.on_next.call_args).to(equal(mock.call('a')))

    with it('yields multi-character solutions'):
      a = _acrostic_iter.Acrostic(list('bag'), BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bag'))

    with it('yields unique solutions'):
      a = _acrostic_iter.Acrostic(list('ba') + ['ggg'], BA_PREFIX_TRIE)
      expect(list(a)).to(have_len(1))

    with it('yields multiple multi-character solutions'):
      a = _acrostic_iter.Acrostic(list('ba') + ['dgnrt'], BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bad', 'bag', 'ban', 'bar', 'bat'))

  with description('_iter_phrases'):
    with before.all:
      self.subject = _acrostic_iter.Acrostic(['a'], tries.letters())

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
      a = _acrostic_iter.Acrostic(list('ba') + ['dgnrt'], BA_PREFIX_TRIE)
      expect(list(a)).to(contain('bad', 'bag', 'ban', 'bar', 'bat'))
      expect(list(a._phrase_graph[0][3].items())).to(equal(
          [('bat', 5), ('bar', 4), ('ban', 3), ('bag', 2), ('bad', 1)]
      ))

  with context('when given ambiguous input text'):
    with it('finds multiple words'):
      a = _acrostic_iter.Acrostic(list('superbowl'), tries.ambiguous())
      expect(list(a)).to(contain('super bowl', 'superb owl', 'superbowl'))

    with it('finds multiple words in really long string'):
      text = 'superbowlwarplanesnapshotscrapbookisnowhere'
      a = _acrostic_iter.Acrostic(list(text), tries.ambiguous())
      expect(''.join(next(iter(a)).split())).to(equal(text))

    with it('finds same answer quickly'):
      text = 'superbowlwarplanesnapshotscrapbookisnowhere'
      a = _acrostic_iter.Acrostic(list(text), tries.ambiguous())
      first = next(iter(a))
      # Result should be cached and '_walk' should never be needed.
      with patch.object(a, '_walk', side_effect=[]) as mock:
        second = next(iter(a))
        expect(first).to(equal(second))
        expect(mock.call_count).to(be_below(10))

    with it('crazy expensive'):
      words = [
        'champion', 'nitpick', 'conspiracy', 'windpipe', 'epinephrine',
        'philanthropic', 'sierpinski', 'mississippi', 'pilaf', 'vulpine',
        'spinach', 'pinochet', 'porcupine', 'megapixels', 'australopithecus',
        'sharpie', 'intrepid', 'insipid', 'robespierre'
      ]
      a = _acrostic_iter.Acrostic(words, tries.everything())
      limit = 1000000
      for i, answer in enumerate(a):
        if answer.startswith('answer') or i % (limit / 10) == 0:
          print(answer)
        if i > limit:
          print('tried %s' % i)
          break
