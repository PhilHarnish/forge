import statistics

from puzzle.problems import problem


class AcrosticProblem(problem.Problem):
  @staticmethod
  def score(lines):
    if len(lines) <= 1:
      return 0
    indexes = _parse_indexes(lines[0])
    if indexes and len(indexes) + 1 == len(lines):
      return 1
    # Apply heuristic.
    num_words = 0
    line_lengths = []
    for line in lines:
      num_words += line.count(' ') + 1
      line_lengths.append(len(line))
    max_line_length = max(line_lengths)
    # Return a perfect score if:
    # - There are more than 4 words.
    # - Average line length is >4 letters.
    # - The words have identical lengths.
    # - There aren't spaces.
    # Max .5 for 2 lines; .75 for 3 lines; 1.0 for 4+ lines.
    num_lines_weight = min(4, len(lines)) / 4
    # Normalize by line length to punish large absolute swings in lengths and
    # forgive +/- 1 character changes for already-long words.
    line_stddev = statistics.stdev([l / max_line_length for l in line_lengths])
    stddev_weight = 1 - line_stddev
    # Punish results with multiple words per line.
    line_length_weight = len(lines) / num_words
    return (num_lines_weight * line_length_weight * stddev_weight *
            line_length_weight)

  def _solve(self):
    return {}


def _parse_indexes(line):
  if not line.startswith('@'):
    return None
  parts = line[1:].split()
  return [int(part) for part in parts]
