from puzzle.heuristics import analyze_word
from spec.mamba import *

with description('analyze_word'):
  with description('score_word'):
    with it('rejects empty input'):
      expect(analyze_word.score_word('')).to(equal(0))

    with it('spots garbage input'):
      expect(analyze_word.score_word('$#!7')).to(equal(0))

    with it('favors known words'):
      for word in ('superbowl', 'super', 'bowl', 'superb', 'owl'):
        expect(call(analyze_word.score_word, word)).to(equal(1))

    with it('scores probable words between (0, 1)'):
      expect(call(analyze_word.score_word, 'probable')).to(be_between(0, 1))

  with description('score_anagram'):
    with it('rejects the same things score_word would'):
      expect(call(analyze_word.score_anagram, '')).to(equal(0))
      expect(call(analyze_word.score_anagram, '$#!7')).to(equal(0))

    with it('rejects words which only anagram to themselves'):
      expect(call(analyze_word.score_anagram, 'bowl')).to(equal(0))

    with it('accepts words which anagram to multiple words'):
      expect(call(analyze_word.score_anagram, 'snap')).to(equal(1))
      expect(call(analyze_word.score_anagram, 'naps')).to(equal(1))

    with it('accepts words which anagram to something else'):
      expect(call(analyze_word.score_anagram, 'lowb')).to(equal(1))

  with description('score_cryptogram'):
    with it('rejects the same things score_word would'):
      expect(call(analyze_word.score_cryptogram, '')).to(equal(0))
      expect(call(analyze_word.score_cryptogram, '$#!7')).to(equal(0))

    with it('rejects 3+ repeated characters'):
      expect(call(analyze_word.score_cryptogram, 'aaabaaa')).to(equal(0))

    with it('rejects words with numerous repeats'):
      expect(call(analyze_word.score_cryptogram, 'banana')).to(be_above(0))
      expect(call(analyze_word.score_cryptogram, 'banananana')).to(equal(0))

    with it('considers jibberish to be plausible'):
      expect(call(analyze_word.score_cryptogram, 'jibberish')).to(be_above(0))
