import sys

from data import warehouse
from puzzle.heuristics import analyze_number
from puzzle.problems import problem

_OFFSETS = None


class NumberProblem(problem.Problem):
  def __init__(self, name, lines, allow_offsets=True):
    super(NumberProblem, self).__init__(name, lines)
    self._value = _parse(lines)
    self._allow_offsets = allow_offsets

  @staticmethod
  def score(lines):
    if not lines:
      return 0
    parsed = _parse(lines)
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
    required_weight = self._threshold
    if self._allow_offsets:
      offsets = _get_offsets()
    else:
      offsets = [0]
    for i, offset in enumerate(offsets):
      scale_factor = 1 - i / len(offsets)
      for (solution, weight), notes in analyze_number.solutions_with_notes(
              self._value + offset):
        if offset:
          solution_str = '%s +%s' % (solution, offset)
        else:
          solution_str = solution
        result[solution_str] = weight * scale_factor
        if offset:
          self._notes[solution_str].append('offset +%s' % offset)
        self._notes[solution_str] += notes
        required_weight = max(weight, required_weight)
      if required_weight == 1:
        break  # Good enough.
      elif scale_factor < required_weight:
        break  # Scale factor will prevent finding anything better.
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
    return digits[0]
  # Well formed data heuristic.
  if len(segment_lengths) == len(bases) and len(bases) == len(digits):
    target_length = segment_lengths[0]
    target_base = bases[0]
    length = len(digits)
    if (all(segment_lengths[i] == target_length for i in range(length)) and
      all(bases[i] == target_base for i in range(length))):
      # This data should be considered well formed already.
      max_digit = target_base ** target_length
  if len(digits) >= 30:  # Chosen arbitrarily.
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
