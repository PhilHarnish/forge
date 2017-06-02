from data import warehouse
from data.seek_sets import crypto_seek_set
from puzzle.problems import problem

# Humans will often choose a ROT value which is ~180 degrees away from A=A.
# For example: ROT13 is common and ROT1 or ROT25 are very uncommon.
_ROT_OFFSETS = list(sorted(range(1, 25), key=lambda i: abs(26 / 2 - i)))
_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
_ALPHABET_UPPER = _ALPHABET.upper()
_ROT_TRANSLATIONS = [None] + [
  str.maketrans(_ALPHABET, _ALPHABET[i:] + _ALPHABET[:i]) for i in range(1, 26)
]
# At least 1/5th of the words must convert.
_MIN_CONVERSION = 0.2
# Minimum threshold for an "interesting" translation.
_MIN_WORD_THRESHOLD = 45000
# Minimum number of characters to consider "translated".
_MIN_WORD = 3
# If Trie yields results greater than this per character it is "good".
_TARGET_WORD_SCORE_RATE = 200000000


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
    good_match = False
    for solution, weight in _generate_rot_n(all_text, self._words):
      good_match = good_match or weight == 1
      yield solution, weight
    if good_match:
      return
    for solution in _generate_partitioned_cryptograms(all_text, self._words):
      yield solution

  def _solve(self):
    raise NotImplementedError()


def _parse(lines):
  tokens = ' '.join(lines).lower().split()
  return tokens, list(filter(str.isalpha, tokens))


def _generate_rot_n(all_text, words):
  for offset in _ROT_OFFSETS:
    score = rot_n_score(words, offset)
    if score > _MIN_CONVERSION:
      solution = all_text.translate(_ROT_TRANSLATIONS[offset])
      yield '%s (rot%s)' % (solution, offset), score


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


def _generate_partitioned_cryptograms(all_text, words):
  # Focus on the longest words.
  sorted_words = sorted(set(words), key=lambda x: -len(x))
  trie = warehouse.get('/words/unigram/trie')
  # Note: This score currently includes whitespace etc.
  target_score = len(all_text) * _TARGET_WORD_SCORE_RATE
  for trans, score in _partitioned_cryptograms_from(sorted_words, [], trie):
    yield all_text.translate(trans), min(1, score / target_score)


def _partitioned_cryptograms_from(crypto_words, normal_words, trie):
  pos = len(normal_words)
  end = len(crypto_words) - 1
  translation = _make_translation(crypto_words, normal_words)
  seek_set = crypto_seek_set.CryptoSeekSet(
      crypto_words[pos], translation=translation)
  for word, score in trie.walk(seek_set, exact_match=True):
    normal_words.append(word)
    if pos == end:
      yield _make_solution_translation_table(translation, crypto_words[pos],
          normal_words[pos]), score
    else:
      for solution, child_score in _partitioned_cryptograms_from(
          crypto_words, normal_words, trie):
        # Up the trampoline, accumulating score.
        yield solution, score + child_score
    normal_words.pop()


def _make_translation(crypto_words, normal_words):
  translation = {}
  for crypto_word, normal_word in zip(crypto_words, normal_words):
    for crypto_c, normal_c in zip(crypto_word, normal_word):
      if crypto_c in translation and translation[crypto_c] != normal_c:
        raise IndexError('Inconsistent translation %s -> %s' % (
          crypto_words, normal_words))
      translation[crypto_c] = normal_c
  return translation


def _make_solution_translation_table(translation, last_crypto, last_word):
  table = str.maketrans(translation)
  table.update(str.maketrans(last_crypto, last_word))
  # Determine upper case letters too.
  table.update(
      str.maketrans(_ALPHABET_UPPER, _ALPHABET.translate(table).upper()))
  return table
