from data import warehouse
from puzzle.problems import problem


class CryptogramProblem(problem.Problem):
  @staticmethod
  def score(lines):
    # Look at all of the "words" in all lines.
    tokens = ' '.join(lines).split()
    if not tokens:
      return 0
    words = list(filter(str.isalpha, tokens))
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

  def _solve(self):
    return {}
