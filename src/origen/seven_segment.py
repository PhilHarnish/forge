from collections import namedtuple

Glyph = namedtuple('Glyph', ['ascii', 'segments'])


def load(s):
  lines = s.split('\n')
  acc = []
  result = {}
  def maybe_flush(acc):
    if not acc:
      return
    segment = parse('\n'.join(acc))
    result[segment.ascii] = segment
    del acc[:]  # Mutate "acc" in place (vs global + reassign).

  for line in lines:
    if line.startswith('>'):
      maybe_flush(acc)
    acc.append(line)
  maybe_flush(acc)
  return result


def parse(s):
  lines = s.split('\n')
  ascii, lines = lines[0].lstrip('>'), lines[1:]
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
  return Glyph(ascii, segments)


def _initialize_segments(lines):
  """Returns list([0, ...n]) for n = max length in lines."""
  return [0] * max([len(line) for line in lines])
