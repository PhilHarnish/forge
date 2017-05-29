import collections

from data import chain, crossword
from data.alphabets import cryptic_keywords
from puzzle.problems.crossword import _base_crossword_problem


class CrypticProblem(_base_crossword_problem._BaseCrosswordProblem):
  def __init__(self, name, lines):
    super(CrypticProblem, self).__init__(name, lines)
    parsed, plan = _compile(lines[0])
    self._tokens = chain.Chain(parsed)
    self._plan = plan

  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    line = lines[0]
    parts = line.split()
    if any(part in cryptic_keywords.ALL_INDICATORS for part in parts):
      return 1
    return _base_crossword_problem.score(lines) * .9  # Lower than normal.

  def _solve(self):
    solutions = _Solutions(self._min_length, self._max_length)
    _visit(self._tokens, self._plan, solutions)
    return solutions


def _compile(clue):
  result = []
  indicators_seen = collections.defaultdict(list)
  for i, token in enumerate(crossword.tokenize_clue(clue)):
    if token in cryptic_keywords.ALL_INDICATORS:
      for indicator in cryptic_keywords.ALL_INDICATORS[token]:
        indicators_seen[indicator].append(i)
    result.append([token])
  plan = sorted(indicators_seen.items(), key=lambda i: _VISIT_ORDER[i[0]])
  return result, plan


def _visit(tokens, plan, solutions):
  # First pass: perform any necessary expansions.
  for _, words in tokens.items():
    source = words[0]
    if source in cryptic_keywords.SHORTHAND_CONVERSIONS:
      words.extend(cryptic_keywords.SHORTHAND_CONVERSIONS[source])
  for indicator, positions in plan:
    try:
      _VISIT_MAP[indicator](tokens, positions, solutions)
    except NotImplementedError:
      print('Indicator for "%s" not implemented' % indicator)
      raise
      # TODO: look for solutions hidden in graph of words.


def _visit_initial(tokens, positions, solutions):
  del solutions  # Initial indicator produces more tokens.
  for position in positions:
    tokens.pop(position)
  for _, words in tokens.items():
    source = words[0]
    words.append(source[0])
  for position in reversed(positions):
    tokens.restore(position)


def _visit_anagram(tokens, positions, solutions):
  end = len(tokens)
  min_length = solutions.min_length
  max_length = solutions.max_length
  anagram_positions = set(positions)

  def _add(acc):
    parts = []  # TODO: Actually perorm anagram.
    banned_matches = 0
    for word, pos in acc:
      parts.append(word)
      if pos in anagram_positions:
        banned_matches += 1
    # Score is 0 if all acc are from possitions; .5 if 1/2 are, etc.
    if not anagram_positions:
      score = 1
    else:
      score = 1 - (banned_matches / len(anagram_positions))
    solutions[''.join(parts)] = score

  def _crawl(pos, acc, acc_length):
    # Try to form total word from all remaining words.
    for i in range(pos, end):
      words = tokens[i]
      for word in words:
        word_length = len(word)
        new_length = acc_length + word_length
        if new_length > max_length:
          continue
        acc_length = new_length
        acc.append((word, i))
        if new_length >= min_length and new_length <= max_length:
          _add(acc)
        elif new_length < max_length:
          _crawl(i + 1, acc, acc_length)
        acc_length -= word_length
        acc.pop()

  _crawl(0, [], 0)


def _visit_concatenate(tokens, positions, solutions):
  end = len(tokens)
  min_length = solutions.min_length
  max_length = solutions.max_length
  concatenate_positions = set(positions)

  def _add(acc):
    if len(acc) == 1:
      return  # Ignore complete words in input.
    parts = []  # TODO: Actually verify word is valid.
    banned_matches = 0
    for word, pos in acc:
      parts.append(word)
      if pos in concatenate_positions:
        banned_matches += 1
    # Score is 0 if all acc are from possitions; .5 if 1/2 are, etc.
    if not concatenate_positions:
      score = 1
    else:
      score = 1 - (banned_matches / len(concatenate_positions))
    solutions[''.join(parts)] = score

  def _crawl(pos, acc, acc_length):
    if pos in concatenate_positions and pos + 1 < end:
      # Optionally, skip ahead to next position using current acc.
      _crawl(pos + 1, acc, acc_length)
    # Try to form total word from all remaining starting points.
    for i in range(pos, end):
      words = tokens[i]
      for word in words:
        word_length = len(word)
        new_length = acc_length + word_length
        if new_length > max_length:
          continue
        acc_length = new_length
        acc.append((word, i))
        if new_length >= min_length and new_length <= max_length:
          _add(acc)
        elif new_length < max_length:
          _crawl(i + 1, acc, acc_length)
        acc_length -= word_length
        acc.pop()

  _crawl(0, [], 0)


def _todo_indicator(*args, **kwargs):
  del args, kwargs
  raise NotImplementedError()


class _Solutions(dict):
  def __init__(self, min_length, max_length):
    super(_Solutions, self).__init__()
    self.min_length = min_length
    self.max_length = max_length


_VISIT_MAP = collections.OrderedDict([
  # Producers.
  (cryptic_keywords.INITIAL_INDICATORS, _visit_initial),
  (cryptic_keywords.EDGES_INDICATORS, _todo_indicator),
  (cryptic_keywords.REVERSAL_INDICATORS, _todo_indicator),
  (cryptic_keywords.TRUNCATION_INDICATORS, _todo_indicator),
  # Reducers.
  (cryptic_keywords.EMBEDDED_INDICATORS, _todo_indicator),
  (cryptic_keywords.ANAGRAM_INDICATORS, _visit_anagram),
  # TODO: Implement these.
  (cryptic_keywords.CONCATENATE_INDICATORS, _visit_concatenate),
  (cryptic_keywords.INSERT_INDICATORS, _todo_indicator),
  (cryptic_keywords.HOMOPHONE_INDICATORS, _todo_indicator),
])
_VISIT_ORDER = dict([(indicator, i) for i, indicator in enumerate(_VISIT_MAP)])
