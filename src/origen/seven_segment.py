from src.origen import data

class Glyph(object):

  def __init__(self, name, lines):
    self.name = name
    self.lines = lines
    self.segments = _parse(lines)


def load(lines):
  return data.load_lines(lines, Glyph)


def _parse(lines):
  segments = _initialize_segments(lines)
  y = 0
  for idx, line in enumerate(lines):
    if idx % 2 == 1:  # Odd (vertical) lines.
      start = 0
    else:  # Even (horizontal) lines.
      start = 1
    x = start
    for c in range(start, len(line), 2):
      if line[c] != ' ':
        segments[x] |= 1 << y
      x += 2
    y += idx % 2  # Increase by one every 2 rows.
  return segments


def _initialize_segments(lines):
  """Returns list([0, ...n]) for n = max length in lines."""
  return [0] * max([len(line) for line in lines])
