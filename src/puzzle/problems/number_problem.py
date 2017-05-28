import sys

from data import warehouse
from puzzle.heuristics import analyze_number
from puzzle.problems import problem

_OFFSETS = None


class NumberProblem(problem.Problem):
  def __init__(self, name, lines):
    super(NumberProblem, self).__init__(name, lines)
    if len(lines) > 1:
      raise NotImplementedError()
    self._value = _parse(lines[0])

  @staticmethod
  def score(lines):
    if not lines:
      return 0
    elif len(lines) > 1:
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
    best_weight = 0.0
    offsets = _get_offsets()
    for i, offset in enumerate(offsets):
      scale_factor = 1 - i / len(offsets)
      for solution, weight in analyze_number.solutions(self._value + offset):
        if offset:
          solution_str = '%s +%s' % (solution, offset)
        else:
          solution_str = solution
        result[solution_str] = weight * scale_factor
        best_weight = max(weight, best_weight)
      if best_weight == 1:
        break  # Good enough.
      elif scale_factor < best_weight:
        break  # Scale factor will prevent finding anything better.
    return result


def _parse(src):
  """Converts a space-separated list of digits into 1 number."""
  if not src:
    return None
  segments = src.split()
  digits = []
  max_digit = 0
  binary_heuristic = True
  for segment in segments:
    if not all(c in '01' for c in segment):
      binary_heuristic = False
      break
  if binary_heuristic:
    max_digit = 2 ** max(len(segment) for segment in segments)
  for segment in segments:
    try:
      if binary_heuristic:
        base = 2
      elif segment.startswith('0x'):
        base = 16
      elif segment.startswith('0'):
        base = 8
      else:
        base = 0  # Autodetect.
      parsed = int(segment, base)
      digits.append(parsed)
      if parsed > max_digit:
        max_digit = parsed
    except:
      # TODO: Support float, base64.
      return None
  if not digits:
    return None
  if len(digits) == 1:
    return digits[0]
  if len(digits) >= 30:  # Chosen arbitrarily.
    return None
  if max_digit > 35:  # Chosen arbitrarily.
    return None
  result = 0
  while digits:
    result *= max_digit
    result += digits.pop(0)
  return result


def _get_offsets():
  global _OFFSETS
  if _OFFSETS is None:
    _OFFSETS = [0] + [
      ord(c) - ord('a') + 1 for c in warehouse.get('/letter/frequency')
    ]
  return _OFFSETS
