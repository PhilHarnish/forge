import collections
import itertools
from typing import Iterable, List, NamedTuple, Optional, Tuple

from data import max_heap
from data.alphabets import morse
from puzzle.problems import problem
from puzzle.steps import generate_solutions

_IGNORE_DELIMITER = 'ignored'
_CHARACTER_DELIMITER = 'character delimiter'
_WORD_DELIMITER = 'word delimiter'
_DOT = '.'
_DASH = '-'
_MORSE_DENSITY = 3.3  # Typical number of morse characters per character.
_TARGET_WORD_LENGTH = 3  # Require 3+ letters.
_TARGET_LENGTH = _MORSE_DENSITY * _TARGET_WORD_LENGTH


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

  def _solve(self) -> dict:
    raise NotImplementedError()  # Explicitly unsupported.

  def _solve_iter(self) -> generate_solutions.Solutions:
    fringe: max_heap.MaxHeap[Tuple[generate_solutions.Solutions, str, bool]] = (
      max_heap.MaxHeap())
    solution_buffer: max_heap.MaxHeap[generate_solutions.Solutions] = (
      max_heap.MaxHeap())
    # Initialize options with weights.
    for weight, interpretation in _generate_interpretations(self._normalized):
      fringe.push(weight, self._iter_interpretation(interpretation))
    while fringe:
      group_generator, group_weight = fringe.pop_with_weight()
      if fringe:
        next_best_weight = fringe.best_weight()
      else:
        next_best_weight = float('-inf')
      while next_best_weight < self._solution_constraints.weight_threshold:
        yield StopIteration()  # Good solutions are impossible.
      yield from solution_buffer.pop_with_weight_until(next_best_weight)
      for result in group_generator:
        (solution, weight), notes, has_ignored = result
        if has_ignored and solution in self._notes:
          continue  # Skip duplicates which can occur with ignored characters.
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
      self, interpretation: _Interpretation
  ) -> Tuple[generate_solutions.Solutions, str, bool]:
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
        return  # TODO: Attempt inserting delimiters.
    solution = (''.join(result), 1.0)
    yield (
      solution, _interpretation_notes(interpretation),
      bool(interpretation.ignored))


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
    margin_of_error = 0.1
  elif len(counts) < len(_ALPHABET) - 1:  # No ignored symbols
    margin_of_error = 0.5
  else:
    margin_of_error = 1.0
  # Increase confidence asymptotically with the size of input. Long inputs
  # with only 3 symbols are very morse-like.
  return max((
    0, (1 - margin_of_error) + (margin_of_error * (1 - _TARGET_LENGTH / size))
  ))


def _generate_interpretations(
    given: str) -> Iterable[Tuple[float, _Interpretation]]:
  results = []
  frequencies = collections.Counter(given)
  (_, first_n), (_, second_n) = frequencies.most_common(2)
  max_score = first_n * first_n + second_n + 1  # +1 to reserve true 1.0.
  def _scored_interpretation(
      dot: str, dash: str, character_delimiter: Optional[str],
      word_delimiter: Optional[str], ignored: set, weight_penalty: float,
  ) -> Tuple[float, _Interpretation]:
    interpretation = _Interpretation(
        dot, dash, character_delimiter, word_delimiter, ignored)
    if dot == '.' and dash == '-':
      # Very probable assignment.
      base_score = max_score
    else:
      base_score = (first_n * frequencies[dot] + frequencies[dash])
      if dot == '-' and dash == '.':
        # Improbable but interesting assignment.
        base_score *= 0.8
    if ignored and not word_delimiter:
      penalty = len(ignored)  # Discourage wasted characters.
    else:
      penalty = 0
    # Prefer assigning (dot, dash) to 1st and 2nd most common, respectively.
    return (
      weight_penalty * base_score / (max_score + penalty),
      interpretation,
    )
  n_chars = len(frequencies)
  for x, y in itertools.combinations(frequencies, 2):
    if n_chars == 2:
      character_delimiter = None
      word_delimiter = None
      ignored = set()
      results.append(_scored_interpretation(
          x, y, character_delimiter, word_delimiter, ignored, 1.0))
      results.append(_scored_interpretation(
          y, x, character_delimiter, word_delimiter, ignored, 1.0))
    elif n_chars == 3:
      character_delimiter = None
      for c in frequencies:
        if c in (x, y):
          continue
        character_delimiter = c
        break
      # Ensure character_delimiter is never consecutive.
      if character_delimiter * 2 in given:
        continue  # Repeated delimiter appears in input.
      word_delimiter = None
      ignored = set()
      results.append(_scored_interpretation(
          x, y, character_delimiter, word_delimiter, ignored, 1.0))
      results.append(_scored_interpretation(
          y, x, character_delimiter, word_delimiter, ignored, 1.0))
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
        if given[-1] == word_delimiter:
          continue  # This interpretation would require a space at the end.
        need_char = False  # Allow arbitrary delimiters to start.
        saw_word_delimiter = False  # Require character between word_delimiter.
        max_word_length = 0
        acc_word_length = 0
        for c in given:
          if c != word_delimiter:
            pass
          elif saw_word_delimiter:
            break  # Two word delimiters occurred between a character.
          else:
            saw_word_delimiter = True
            max_word_length = max(acc_word_length, max_word_length)
            acc_word_length = 0
          if c in (x, y):
            need_char = False  # Found a character. Reset expectations.
            saw_word_delimiter = False
            acc_word_length += 1
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
          if given.startswith(word_delimiter) or given.endswith(word_delimiter):
            weight_penalty = 0.25
          else:
            weight_penalty = 1.0
          if max_word_length < _TARGET_WORD_LENGTH:
            weight_penalty *= 0.1
          results.append(_scored_interpretation(
              x, y, character_delimiter, word_delimiter, ignored,
              weight_penalty))
          results.append(_scored_interpretation(
              y, x, character_delimiter, word_delimiter, ignored,
              weight_penalty))
          # Perhaps word delimiters are ignored.
          ignored = ignored.copy()
          ignored.add(word_delimiter)
          results.append(_scored_interpretation(
              x, y, character_delimiter, None, ignored, weight_penalty * 0.9))
          results.append(_scored_interpretation(
              y, x, character_delimiter, None, ignored, weight_penalty * 0.9))
          # Perhaps all delimiters are ignored.
          ignored = ignored.copy()
          ignored.add(character_delimiter)
          results.append(_scored_interpretation(
              x, y, None, None, ignored, weight_penalty * 0.8))
          results.append(_scored_interpretation(
              y, x, None, None, ignored, weight_penalty * 0.8))
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
