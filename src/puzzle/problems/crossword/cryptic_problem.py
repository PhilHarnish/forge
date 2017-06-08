import collections

from data import chain, crossword, warehouse
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
  words_api = warehouse.get('/api/words')
  # First pass: perform any necessary expansions.
  for _, words in tokens.items():
    source = words[0]
    if source in cryptic_keywords.SHORTHAND_CONVERSIONS:
      words.extend(cryptic_keywords.SHORTHAND_CONVERSIONS[source])
    words.extend(words_api.expand(source).keys())
  for indicator, positions in plan:
    try:
      _VISIT_MAP[indicator](tokens, positions, solutions)
    except NotImplementedError:
      print('Indicator for "%s" not implemented' % indicator)
      raise
  if not solutions:
    # Finally, attempt to find the solution from pieces of the expanded words.
    _visit_concatenate(tokens, [], solutions)


def _visit_initial(tokens, positions, solutions):
  del solutions  # Initial indicator produces more tokens.
  for position in positions:
    tokens.pop(position)
  for _, words in tokens.items():
    source = words[0]
    words.append(source[0])
  for position in reversed(positions):
    tokens.restore(position)


def _visit_edges(tokens, positions, solutions):
  del solutions  # Initial indicator produces more tokens.
  for position in positions:
    tokens.pop(position)
  for _, words in tokens.items():
    source = words[0]
    words.append(source[0] + source[-1])
  for position in reversed(positions):
    tokens.restore(position)


def _visit_reversal(tokens, positions, solutions):
  del solutions  # Initial indicator produces more tokens.
  for position in positions:
    tokens.pop(position)
  for _, words in tokens.items():
    source = words[0]
    words.append(''.join(reversed(source)))
  for position in reversed(positions):
    tokens.restore(position)


def _visit_embedded(tokens, positions, solutions):
  min_length = solutions.min_length
  max_length = solutions.max_length
  acc = []
  pos_map = []
  start_map = []
  for pos, tokens in tokens.items():
    source = tokens[0]
    acc.append(source)
    for i in range(len(source)):
      pos_map.append(pos)
      start_map.append(i == 0)
  search_text = ''.join(acc)
  trie = warehouse.get('/words/unigram/trie')
  interesting_threshold = trie.interesting_threshold()
  end = len(search_text) - min_length
  ignored = set(acc)  # Ignore words from clue itself.
  for offset in range(end):
    for result, weight in trie.walk(search_text[offset:]):
      if result in ignored:
        continue
      result_length = len(result)
      if result_length >= min_length and result_length <= max_length:
        base_weight = min(1, weight / interesting_threshold)
        # Demote scores for start-of-word.
        if start_map[offset]:
          base_weight *= .9
        # Score = % of word not banned by `positions`.
        solutions[result] = base_weight * (
                              sum(i not in positions for i in
                              range(offset, offset + result_length))
                            ) / result_length


def _visit_anagram(tokens, positions, solutions):
  end = len(tokens)
  min_length = solutions.min_length
  max_length = solutions.max_length
  anagram_positions = set(positions)
  anagram_index = warehouse.get('/words/unigram/anagram_index')
  trie = warehouse.get('/words/unigram/trie')
  interesting_threshold = trie.interesting_threshold()
  banned_max = len(anagram_positions)

  def _add(acc, banned_max):
    parts = []
    banned_matches = 0
    for word, pos in acc:
      parts.append(word)
      if pos in anagram_positions:
        banned_matches += 1
      elif word in cryptic_keywords.CONCATENATE_INDICATORS:
        # Special case for concatenate keywords which frequently join two
        # chunks of an anagram.
        banned_matches += 1
        banned_max += 1
    solution = ''.join(parts)
    if solution not in anagram_index:
      return
    anagrams = anagram_index[solution]
    # Score is 0 if all acc are from possitions; .5 if 1/2 are, etc.
    if not anagram_positions:
      score = 1
    else:
      score = 1 - (banned_matches / banned_max)
    for anagram in anagrams:
      if anagram != solution:
        base_weight = min(1, trie[anagram] / interesting_threshold)
        solutions[anagram] = base_weight * score

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
          _add(acc, banned_max)
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
  trie = warehouse.get('/words/unigram/trie')
  interesting_threshold = trie.interesting_threshold()

  def _add(acc):
    if len(acc) == 1:
      return  # Ignore complete words in input.
    parts = []
    banned_matches = 0
    for word, pos in acc:
      parts.append(word)
      if pos in concatenate_positions:
        banned_matches += 1
    solution = ''.join(parts)
    if solution not in trie:
      return
    # Score is 0 if all acc are from possitions; .5 if 1/2 are, etc.
    if not concatenate_positions:
      score = 1
    else:
      score = 1 - (banned_matches / len(concatenate_positions))
    base_weight = min(1, trie[solution] / interesting_threshold)
    solutions[solution] = base_weight * score

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
        elif new_length < max_length and trie.has_keys_with_prefix(
            ''.join(a[0] for a in acc)):
          _crawl(i + 1, acc, acc_length)
        acc_length -= word_length
        acc.pop()

  _crawl(0, [], 0)


def _visit_homophone(tokens, positions, solutions):
  del tokens, positions
  if not solutions:
    raise NotImplementedError('Homophones not implemented')


def _visit_insert(tokens, positions, solutions):
  if not solutions:
    # "INSERT" indicator is usually a subset of functionality provided by
    # "ANAGRAM".
    _visit_anagram(tokens, positions, solutions)
  if not solutions:
    raise NotImplementedError()


class _Solutions(dict):
  def __init__(self, min_length, max_length):
    super(_Solutions, self).__init__()
    self.min_length = min_length
    self.max_length = max_length


_VISIT_MAP = collections.OrderedDict([
  # Embedded clues only use original words.
  (cryptic_keywords.EMBEDDED_INDICATORS, _visit_embedded),
  # Producers.
  (cryptic_keywords.INITIAL_INDICATORS, _visit_initial),
  (cryptic_keywords.EDGES_INDICATORS, _visit_edges),
  (cryptic_keywords.REVERSAL_INDICATORS, _visit_reversal),
  # Reducers.
  (cryptic_keywords.ANAGRAM_INDICATORS, _visit_anagram),
  # TODO: Incomplete implementation. Redundant with anagram indicator.
  (cryptic_keywords.INSERT_INDICATORS, _visit_insert),
  (cryptic_keywords.CONCATENATE_INDICATORS, _visit_concatenate),
  # TODO: Incomplete implementation. This should be up with "producers".
  (cryptic_keywords.HOMOPHONE_INDICATORS, _visit_homophone),
])
_VISIT_ORDER = dict([(indicator, i) for i, indicator in enumerate(_VISIT_MAP)])
