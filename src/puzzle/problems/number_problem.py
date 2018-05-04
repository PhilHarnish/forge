import sys

from data import warehouse
from puzzle.heuristics import analyze_number
from puzzle.problems import problem

_OFFSETS = None


class NumberProblem(problem.Problem):
  def __init__(self, name, lines, allow_offsets=True, **kwargs):
    super(NumberProblem, self).__init__(name, lines, **kwargs)
    self._digits = _parse(lines)
    self._allow_offsets = allow_offsets

  @staticmethod
  def score(lines):
    if not lines:
      return 0
    parsed = _parse(lines)
    if not parsed:
      return 0
    if any(isinstance(digit, float) for digit in parsed):
      return .5  # Unsure how to score a float.
    if len(parsed) > 5:
      return 1  # Enough digits to be interesting.
    # Weakest score returned for 0 ('epsilon').
    max_information = max(parsed) ** len(parsed)
    return max(sys.float_info.epsilon, min(max_information / 0xAAAA, 1))

  def _solve(self):
    # TODO: Much optimization needed here.
    result = {}
    required_weight = self._threshold
    if self._allow_offsets and len(self._digits) == 1:
      offsets = _get_offsets()
    else:
      offsets = [0]
    for i, offset in enumerate(offsets):
      scale_factor = 1 - i / len(offsets)
      digits = self._digits[:]
      if offset:
        digits[0] += offset
      for (
      solution, weight), notes in analyze_number.digit_solutions_with_notes(
          digits):
        scaled_weight = weight * scale_factor
        if scaled_weight < required_weight:
          continue
        if offset:
          solution_str = '%s +%s' % (solution, offset)
        else:
          solution_str = solution
        result[solution_str] = scaled_weight
        if offset:
          self._notes[solution_str].append('offset +%s' % offset)
        self._notes[solution_str] += notes
    return result


def _parse(lines):
  """Converts a space-separated list of digits into 1 number."""
  if not lines:
    return None
  segments = ' '.join(lines).split()  # Merge into one line.
  if not segments:
    return None
  digits = []
  bases = []
  segment_lengths = []
  max_digit = 0
  binary_heuristic = True
  for segment in segments:
    if not all(c in '01' for c in segment):
      binary_heuristic = False
      break
  for segment in segments:
    segment_length = len(segment)
    try:
      if binary_heuristic:
        base = 2
      elif segment.startswith('0x'):
        base = 16
        segment_length -= 2
      elif segment.startswith('0'):
        base = 8
        segment_length -= 1
      else:
        base = 0  # Autodetect.
      segment_lengths.append(segment_length)
      bases.append(base)
      parsed = int(segment, base)
      digits.append(parsed)
      if parsed > max_digit:
        max_digit = parsed + 1
    except:
      # TODO: Support float, base64.
      return None
  if not digits:
    return None
  if len(digits) == 1:
    return digits
  if len(digits) >= 30:  # Chosen arbitrarily.
    return None
  return digits


def _get_offsets():
  global _OFFSETS
  if _OFFSETS is None:
    _OFFSETS = [0] + [
      ord(c) - ord('a') + 1 for c in warehouse.get('/letter/frequency')
    ]
  return _OFFSETS
