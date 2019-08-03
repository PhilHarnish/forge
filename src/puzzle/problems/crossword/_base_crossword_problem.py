import re

from data.alphabets import crossword_indicators
from puzzle.problems import problem

_CROSSWORD_REGEX = re.compile(r'^.*\(([\d\s,|]+)? ?(wo?r?ds)?(hyphe?n?)?\.?\)$')
_ADDRESS = re.compile(r'\s*\d+\.\s')
_INT_REGEX = re.compile(r'(\d+)')


class _BaseCrosswordProblem(problem.Problem):
  def __init__(self, name: str, lines: problem.ProblemData, **kwargs) -> None:
    if len(lines) > 1:
      raise NotImplementedError('Only one crossword clue per problem')
    lines = [_clean(line) for line in lines]
    super(_BaseCrosswordProblem, self).__init__(name, lines, **kwargs)
    self._min_length = 1
    self._max_length = float('inf')
    for line in lines:
      for match in _CROSSWORD_REGEX.finditer(line):
        int_constraint, word_constraint, hyphen_constraint = match.groups()
        if int_constraint is None:
          break
        lengths = _INT_REGEX.findall(int_constraint)
        if word_constraint:
          # TODO: Verify word_constraint, hyphen_constraint.
          pass
        elif len(lengths) == 1:
          target = int(lengths[0])
          self._solution_constraints.solution_length = target
          self._min_length = target
          self._max_length = target
        else:
          target = sum(map(int, lengths))
          if '|' in line:
            self._solution_constraints.solution_min_length = target
            self._min_length = target
            self._max_length = float('inf')
          else:
            # TODO: Verify 2, 3 -> 2 letter word & 3 letter word.
            self._solution_constraints.solution_length = target
            self._min_length = target
            self._max_length = target
        break

  def _solve(self) -> dict:
    raise NotImplementedError()

def score(lines: problem.ProblemData) -> float:
  if len(lines) > 1:
    return 0
  src = next(iter(lines))
  if _CROSSWORD_REGEX.match(src):
    return 1
  words = src.split()
  # Remove common pieces of punctuation when considering words.
  num_words = sum(word.strip('"\',.').isalpha() for word in words)
  if num_words < len(words) / 2:
    return 0
  if set(words).intersection(crossword_indicators.CROSSWORD_INDICATORS):
    base_score = 1
  else:
    base_score = 0.5
  # Something with a lot of words *might* be a crossword clue.
  return base_score * (min(5, num_words) / 5)


def _clean(line: str) -> str:
  # Remove leading/trailing whitespace.
  line = line.strip()
  # Remove leading "12. "
  line = re.sub(_ADDRESS, '', line)
  return line
