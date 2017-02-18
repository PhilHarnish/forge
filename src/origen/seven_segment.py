from src.origen import data

class Glyphs(object):

  def __init__(self, name, lines):
    self.name = name
    self.lines = lines  # TODO: Generate dynamically.
    self.segments = _parse(lines)

  def __eq__(self, other):
    if not issubclass(type(other), Glyphs):
      return False
    if len(self.segments) != len(other.segments):
      return False
    return all([a == b for a, b in zip(self.segments, other.segments)])

  def __or__(self, other):
    glyphs = Glyphs('(%s|%s)' % (self.name, other.name), [])
    # Bitwise OR any overlapping segments.
    merged = [a | b for a, b in zip(self.segments, other.segments)]
    # Append any remaining segments.
    merged += self.segments[len(other.segments):]
    merged += other.segments[len(self.segments):]
    glyphs.segments = merged
    return glyphs

  def __add__(self, other):
    glyphs = Glyphs('(%s+%s)' % (self.name, other.name), [])
    if len(self.segments) % 2:
      spacer = [0]
    else:
      spacer = []
    glyphs.segments = self.segments + spacer + other.segments
    return glyphs

  def __lshift__(self, other):
    glyphs = Glyphs('(%s<<%s)' % (self.name, other), [])
    glyphs.segments = self.segments[2 * other:]
    return glyphs

  def __rshift__(self, other):
    glyphs = Glyphs('(%s>>%s)' % (self.name, other), [])
    glyphs.segments = [0]*(2*other) + self.segments
    return glyphs

  def __str__(self):
    return '[%s]\n%s' % (self.name, self.segments)

  def __repr__(self):
    return 'Glyphs("%s", %s)' % (self.name, self.segments)


def load(lines):
  return data.load_lines(lines, Glyphs)


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
  if lines:
    return [0] * max([len(line) for line in lines])
  return []
