import Numberjack
from origen import seven_segment
from origen import seven_segment_data


class AccessPuzzle(object):

  def __init__(self, goal, num_boards):
    self.model = Numberjack.Model()
    self.goal = _make_access_matrix('goal')
    self._set_goal(goal)
    self.key = _make_access_matrix('key')
    self.boards = []
    for i in range(0, num_boards):
      self.boards.append(_make_access_matrix('board%s' % i))
    self._constrain_key()

  def solve(self):
    solver = self.model.load('Mistral')
    solver.solve()

  def get_key(self):
    return _convert_matrix_to_glyphs('key', self.key)

  def get_board(self, idx):
    return _convert_matrix_to_glyphs('board%s' % idx, self.boards[idx])

  def _set_goal(self, goal):
    _constrain_matrix(self.model, self.goal, goal)

  def _constrain_key(self):
    for i, row in enumerate(self.key):
      for j, value in enumerate(row):
        target = self.goal[i][j]
        for board in self.boards:
          self.model.add((value | board[i][j]) == target)


def accept(glyphs):
  return glyphs == seven_segment_data.ACCESS


def _make_access_matrix(name):
  access_length = len(seven_segment_data.ACCESS)
  return Numberjack.Matrix(access_length, 3, name)


def _constrain_matrix(model, matrix, glyphs):
  padding = len(matrix) - len(glyphs)
  for i, segment in enumerate(glyphs.segments + [0] * padding):
    for bit in range(0, 3):
      model.add(matrix[i][bit] == bool(segment & (1 << bit)))


def _convert_matrix_to_glyphs(name, matrix):
  glyphs = seven_segment.Glyphs(name, [])
  for i, row in enumerate(matrix):
    bits = 0
    for j, value in enumerate(row):
      if value.get_value():
        bits |= 1 << j
    glyphs.segments.append(bits)
  return glyphs
