from data import warehouse
from puzzle.problems import problem

# Humans will often choose a ROT value which is ~180 degrees away from A=A.
# For example: ROT13 is common and ROT1 or ROT25 are very uncommon.
_ROT_OFFSETS = list(sorted(range(1, 25), key=lambda i: abs(26 / 2 - i)))
_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
_ROT_TRANSLATIONS = [None] + [
  str.maketrans(_ALPHABET, _ALPHABET[i:] + _ALPHABET[:i]) for i in range(1, 26)
]
# At least 1/5th of the words must convert.
_MIN_CONVERSION = 0.2
# Minimum threshold for an "interesting" translation.
_MIN_WORD_THRESHOLD = 45000
# Minimum number of characters to consider "translated".
_MIN_WORD = 3


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
      score = rot_n_score(self._words, offset)
      if score > _MIN_CONVERSION:
        solution = all_text.translate(_ROT_TRANSLATIONS[offset])
        yield '%s (rot%s)' % (solution, offset), score

  def _solve(self):
    raise NotImplementedError()


def _parse(lines):
  tokens = ' '.join(lines).split()
  return tokens, list(filter(str.isalpha, tokens))


def rot_n_score(words, n):
  """ Score `words` for rotation `n`.
  :param words:
  :param n:
  :return: Returns 1 if every single word translates to a common word.
      If all words are common score decreases proportional to chars translated.
      If all translations are uncommon then
  """
  unigrams = warehouse.get('/words/unigram')
  score = 0
  all = 0
  for word in words:
    l = len(word)
    if l < _MIN_WORD:
      continue
    translated = word.translate(_ROT_TRANSLATIONS[n])
    if translated in unigrams:
      word_weight = min(1, unigrams[translated] / _MIN_WORD_THRESHOLD)
      score += l * word_weight
    all += l
  return score / all
