import sys

from puzzle.heuristics import analyze_number
from puzzle.problems import problem


class NumberProblem(problem.Problem):
  def __init__(self, name, lines):
    super(NumberProblem, self).__init__(name, lines)
    if len(lines) > 1:
      raise NotImplementedError()
    self._value = _parse(lines[0])

  @staticmethod
  def score(lines):
    if len(lines) > 1:
      return 0
    parsed = _parse(lines[0])
    if parsed is None:
      return 0
    if isinstance(parsed, float):
      return .5  # Unsure how to score a float.
    # Weakest score returned for 0 ('epsilon').
    # Smallest 4 letter word can be made with base-16.
    return max(sys.float_info.epsilon, min(parsed / 0xAAAA, 1))

  def _solve(self):
    # TODO: Much optimization needed here.
    result = {}
    for solution, weight in analyze_number.solutions(self._value):
      result[solution] = weight
    return result


def _parse(src):
  result = None
  try:
    if src.startswith('0x'):
      base = 16
    elif src.startswith('0'):
      base = 8
    else:
      base = 0  # Autodetect.
    result = int(src, base)
  except:
    try:
      result = float(src)
    except:
      # TODO: Base64.
      pass
  return result
