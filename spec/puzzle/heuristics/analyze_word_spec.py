from mock.mock import patch

from spec.data.fixtures import tries
from spec.mamba import *

from puzzle.heuristics import analyze_word


with description('analyze_word'):
  with before.all:
    analyze_word.init_trie(tries.ambiguous())

  with description('score'):
    with it('rejects empty input'):
      expect(analyze_word.score_word('')).to(equal(0))

    with it('spots garbage input'):
      expect(analyze_word.score_word('$#!7')).to(equal(0))

    with it('favors known words'):
      for word in tries.ambiguous():
        expect(call(analyze_word.score_word, word)).to(equal(1))

    with it('scores probable words between (0, 1)'):
      expect(analyze_word.score_word('probable')).to(be_between(0, 1))
