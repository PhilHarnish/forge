from data import warehouse
from puzzle.problems import problem

# Humans will often choose a ROT value which is ~180 degrees away from A=A.
# For example: ROT13 is common and ROT1 or ROT25 are very uncommon.
_ROT_OFFSETS = list(sorted(range(1, 25), key=lambda i: abs(26 / 2 - i)))
_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
_ROT_TRANSLATIONS = [None] + [
  str.maketrans(_ALPHABET, _ALPHABET[i:] + _ALPHABET[:i]) for i in range(1, 26)
]


class CryptogramProblem(problem.Problem):
  def __init__(self, name, lines):
    super(CryptogramProblem, self).__init__(name, lines)
    _, self._words = _parse(lines)


  @staticmethod
  def score(lines):
    # Look at all of the "words" in all lines.
    tokens, words = _parse(lines)
    if not words:
      return 0  # Nothing to cryptogram.
    if len(words) < len(tokens) // 2:
      return 0  # Fewer than half of the tokens could be considered words.
    # How many words appear to be gibberish?
    known_words = warehouse.get('/words/unigram')
    are_words = sum(word in known_words for word in words)
    if are_words < len(words) // 8 + 1:
      # Fewer than 1 in 8 of the original words are known.
      return 1
    # Something with 5+ of words *might* be a cryptic clue.
    return max(0.0, 0.25 * (min(5, len(words)) / 5))

  def _solve_iter(self):
    # First attempt a rotN solve.
    all_text = '\n'.join(self.lines)
    for offset in _ROT_OFFSETS:
      if is_rot_n(self._words, offset):
        # Return 1.0 score because a match is (normally) exceptionally rare.
        yield all_text.translate(_ROT_TRANSLATIONS[offset]), 1

  def _solve(self):
    raise NotImplementedError()


def _parse(lines):
  tokens = ' '.join(lines).split()
  return tokens, list(filter(str.isalpha, tokens))


def is_rot_n(words, n):
  unigrams = warehouse.get('/words/unigram')
  return all(word.translate(_ROT_TRANSLATIONS[n]) in unigrams for word in words)
