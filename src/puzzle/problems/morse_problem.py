import collections
import itertools
from typing import Iterable, List, NamedTuple, Optional, Tuple

from data import max_heap
from data.alphabets import morse
from puzzle.problems import problem

_IGNORE_DELIMITER = 'ignored'
_CHARACTER_DELIMITER = 'character delimiter'
_WORD_DELIMITER = 'word delimiter'
_DOT = '.'
_DASH = '-'

class _Interpretation(NamedTuple):
  dot: str
  dash: str
  character_delimiter: Optional[str]
  word_delimiter: Optional[str]
  ignored: set


# "Most common" interpretation.
_ALPHABET = _Interpretation(
    '.',
    '-',
    ' ',
    '/',
    set(),
)


class MorseProblem(problem.Problem):
  def __init__(self, name: str, lines: List[str], **kwargs) -> None:
    super(MorseProblem, self).__init__(name, lines, **kwargs)
    self._normalized = '\n'.join(lines)
    self._frequencies = collections.Counter(self._normalized)
    for c in list(self._frequencies.keys()):
      if c.isspace():  # Ignore whitespace in input.
        del self._frequencies[c]

  @staticmethod
  def score(lines: List[str]) -> float:
    return _score(lines)

  def _solve_iter(self) -> problem.Solutions:
    fringe: max_heap.MaxHeap[problem.Solutions] = max_heap.MaxHeap()
    solution_buffer: max_heap.MaxHeap[problem.Solutions] = max_heap.MaxHeap()
    # Initialize options with weights.
    for weight, interpretation in _generate_interpretations(self._normalized):
      fringe.push(weight, self._iter_interpretation(interpretation))
    while fringe:
      group_generator, group_weight = fringe.pop_with_weight()
      if fringe:
        next_best_weight = fringe.best_weight()
      else:
        next_best_weight = float('-inf')
      yield from solution_buffer.pop_with_weight_until(next_best_weight)
      for result in group_generator:
        (solution, weight), notes = result
        self._notes[solution] = notes  # Save (and throw away) notes.
        solution_weight = group_weight * weight
        if solution_weight > next_best_weight:
          yield solution, solution_weight
        else:
          solution_buffer.push(solution_weight, solution)
          # Abandon this generator for now.
          fringe.push(group_weight, group_generator)
          break
    yield from solution_buffer.pop_with_weight_until(float('-inf'))

  def _iter_interpretation(
      self, interpretation: _Interpretation) -> problem.Solutions:
    acc = []
    result = []
    for c in self._normalized:
      if c == interpretation.dot:
        acc.append('.')
      elif c == interpretation.dash:
        acc.append('-')
      elif c in (
          interpretation.character_delimiter, interpretation.word_delimiter):
        buffer = ''.join(acc)
        acc.clear()
        if not buffer:
          pass
        elif buffer in morse.LOOKUP:
          result.append(morse.LOOKUP[buffer])
        else:
          # Turns out this was an invalid interpretation?
          return
        if c == interpretation.word_delimiter:
          result.append(' ')
      elif c in interpretation.ignored:
        continue
      else:
        raise ValueError(
            'Unexpected "%s" for interpretation %s' % (c, interpretation))
    if acc:
      buffer = ''.join(acc)
      if buffer in morse.LOOKUP:
        result.append(morse.LOOKUP[buffer])
      else:
        return
    solution = (''.join(result), 1.0)
    yield solution, _interpretation_notes(interpretation)


def _score(lines: List[str]) -> float:
  counts = collections.Counter()
  size = 0
  for line in lines:
    counts.update(line)
    size += len(line)
    if len(counts) > len(_ALPHABET):
      return 0
  if len(counts) < 2:
    return 0  # Minimal input.
  # There are [1, _ALPHABET] symbols.
  if all(c in _ALPHABET for c in counts):
    return 1  # Looks like ordinary morse.
  elif '.' in counts and '-' in counts:
    margin_of_error = .1
  else:
    margin_of_error = 1
  # Increase confidence asymptotically with the size of input. Long inputs
  # with only 3 symbols are very morse-like.
  return (1 - margin_of_error) + (margin_of_error * (1 - 1 / size))


def _generate_interpretations(
    given: str) -> Iterable[Tuple[float, _Interpretation]]:
  results = []
  frequencies = collections.Counter(given)
  (_, first_n), (_, second_n) = frequencies.most_common(2)
  max_score = first_n * first_n + second_n + 1  # +1 to reserve true 1.0.
  def _scored_interpretation(
      dot: str, dash: str, character_delimiter: Optional[str],
      word_delimiter: Optional[str], ignored: set
  ) -> Tuple[float, _Interpretation]:
    interpretation = _Interpretation(
        dot, dash, character_delimiter, word_delimiter, ignored)
    if dot == '.' and dash == '-':
      # Very probable assignment.
      base_score = max_score
    else:
      base_score = (first_n * frequencies[dot] + frequencies[dash])
    if ignored and not word_delimiter:
      penalty = len(ignored)  # Discourage wasted characters.
    else:
      penalty = 0
    # Prefer assigning (dot, dash) to 1st and 2nd most common, respectively.
    return (
      base_score / (max_score + penalty),
      interpretation,
    )
  n_chars = len(frequencies)
  for x, y in itertools.combinations(frequencies, 2):
    if n_chars == 2:
      character_delimiter = None
      word_delimiter = None
      ignored = set()
      results.append(_scored_interpretation(
          x, y, character_delimiter, word_delimiter, ignored))
      results.append(_scored_interpretation(
          y, x, character_delimiter, word_delimiter, ignored))
    elif n_chars == 3:
      character_delimiter = None
      for c in frequencies:
        if c in (x, y):
          continue
        character_delimiter = c
        break
      word_delimiter = None
      ignored = set()
      results.append(_scored_interpretation(
          x, y, character_delimiter, word_delimiter, ignored))
      results.append(_scored_interpretation(
          y, x, character_delimiter, word_delimiter, ignored))
    else:
      # Need to choose both a character and word delimiter.
      options = []
      for c in frequencies:
        if c in (x, y):
          continue
        options.append(c)
      # 2+ items in options. Validate delimiters never repeat.
      last = None
      for character_delimiter, word_delimiter in itertools.permutations(
          options, 2):
        need_char = False  # Allow arbitrary delimiters to start.
        saw_word_delimiter = False  # Require character between word_delimiter.
        for c in given:
          if c != word_delimiter:
            pass
          elif saw_word_delimiter:
            break  # Two word delimiters occurred between a character.
          else:
            saw_word_delimiter = True
          if c in (x, y):
            need_char = False  # Found a character. Reset expectations.
            saw_word_delimiter = False
          elif need_char and c == last:
            break  # Needed a character and delimiter repeated. Break.
          elif c in (character_delimiter, word_delimiter):
            need_char = True  # Expect a character.
          last = c
        else:
          # 'break' never happened
          ignored = set()
          for c in options:
            if c in (character_delimiter, word_delimiter):
              continue
            ignored.add(c)
          results.append(_scored_interpretation(
              x, y, character_delimiter, word_delimiter, ignored))
          results.append(_scored_interpretation(
              y, x, character_delimiter, word_delimiter, ignored))
          # Perhaps delimiters are ignored.
          ignored = ignored.copy()
          ignored.add(word_delimiter)
          results.append(_scored_interpretation(
              x, y, character_delimiter, None, ignored))
          results.append(_scored_interpretation(
              y, x, character_delimiter, None, ignored))
          ignored = ignored.copy()
          ignored.add(character_delimiter)
          results.append(_scored_interpretation(
              x, y, None, None, ignored))
          results.append(_scored_interpretation(
              y, x, None, None, ignored))
  return sorted(results, key=lambda key: key[0], reverse=True)


def _interpretation_notes(interpretation) -> List[str]:
  parts = [
    'dot: %s' % repr(interpretation.dot),
    'dash: %s' % repr(interpretation.dash),
  ]
  if interpretation.character_delimiter:
    parts.append(
        'character delimiter: %s' % repr(interpretation.character_delimiter))
  if interpretation.word_delimiter:
    parts.append('space: %s' % repr(interpretation.word_delimiter))
  if interpretation.ignored:
    parts.append('ignored: %s' % repr(''.join(sorted(interpretation.ignored))))
  return parts
