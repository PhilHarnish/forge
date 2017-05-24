import Numberjack


class Constraint(object):
  def __init__(self, width, height):
    super(Constraint, self).__setattr__('_model', Numberjack.Model())
    super(Constraint, self).__setattr__('_matrix',
        Numberjack.Matrix(width, height, 0, 9))
    super(Constraint, self).__setattr__('_constraints', {})

  def __setattr__(self, item, value):
    if item in self._constraints:
      raise AttributeError('%s already defined to %s' % (
        item, self._constraints[item]))
    size = self._magnitude(value)
    self._constraints[item] = Numberjack.Variable(
        self._lower(size), self._upper(size), item)
    try:
      (ax, ay), second = value
      if isinstance(second, int):
        if item[0] == 'a':
          (bx, by) = (ax + second - 1, ay)
        else:
          (bx, by) = (ax, ay + second - 1)
      else:
        (bx, by) = second
      (ax, ay), (bx, by) = (ax - 1, ay - 1), (bx - 1, by - 1)
      acc = None
      for x in range(ax, bx + 1):  # Iterate, inclusive.
        for y in range(ay, by + 1):
          if acc is None:
            acc = self._matrix[y][x]
            self._model.add(acc > 0)
          else:
            acc = acc * 10 + self._matrix[y][x]
      self._model.add(self._constraints[item] == acc)
    except TypeError:
      print('No coordinates for %s' % item)

  def _magnitude(self, value):
    try:
      (ax, ay), second = value
      try:
        (bx, by) = second
        if ax != bx and ay != by:
          raise Exception('diagonal %s' % value)
        return (bx - ax) + (by - ay) + 1
      except TypeError:
        return int(second)
    except TypeError:
      return int(value)

  def _match_most_sig_digit(self, a, b):
    if self._sizes[b] > self._sizes[a]:
      self._match_most_sig_digit(b, a)
      return
    a_size = self._sizes[a]
    a_digit = self._constraints[a] - (
      self._constraints[a] % self._lower(a_size))
    b_size = self._sizes[b]
    b_digit = self._constraints[b] - (
      self._constraints[b] % self._lower(b_size))
    while a_size > b_size:
      b_size += 1
      b_digit *= 10
    self._model.add(a_digit == b_digit)

  def _lower(self, size):
    return 10 ** (size - 1)

  def _upper(self, size):
    return 10 ** size - 1

  def __getattr__(self, item):
    if item not in self._constraints:
      raise AttributeError('%s not defined' % item)
    return self._constraints[item]

  def solve(self):
    solver = self._model.load('Mistral')
    solver.solve()
    for y in range(0, 9):
      print(',\t'.join([str(x) for x in self._matrix[y]]))
    for k, v in self._constraints.iteritems():
      print(k, '=', v)
    print('Nodes:', solver.getNodes(), ' Time:', solver.getTime())

  def add(self, expr):
    self._model.add(expr)


p = Constraint(9, 9)
p.a1 = ((1, 1), (3, 1))
p.a3 = ((5, 1), (7, 1))
p.a6 = ((3, 2), (5, 2))
p.a8 = ((7, 2), (9, 2))
p.a10 = ((1, 3), (2, 3))
p.a12 = ((4, 3), (6, 3))
p.a14 = ((8, 3), (9, 3))
p.a15 = ((2, 4), (4, 4))
p.a17 = ((6, 4), (8, 4))
p.a19 = ((2, 6), (4, 6))
p.a21 = ((6, 6), (8, 6))
p.a23 = ((1, 7), (2, 7))
p.a24 = ((4, 7), (6, 7))
p.a26 = ((8, 7), (9, 7))
p.a28 = ((1, 8), 3)
p.a30 = ((5, 8), 3)
p.a32 = ((3, 9), 3)
p.a33 = ((7, 9), 3)

p.d1 = ((1, 1), (1, 3))
p.d2 = ((3, 1), (3, 2))
p.d3 = ((5, 1), (5, 3))
p.d4 = ((7, 1), (7, 2))
p.d5 = ((9, 1), (9, 3))
p.d7 = ((4, 2), (4, 4))
p.d9 = ((8, 2), (8, 4))
p.d11 = ((2, 3), (2, 4))
p.d13 = ((6, 3), 2)
p.d16 = ((3, 4), 3)
p.d18 = ((7, 4), 3)
p.d19 = ((2, 6), 3)
p.d20 = ((4, 6), 2)
p.d21 = ((6, 6), (6, 8))
p.d22 = ((8, 6), 2)
p.d23 = ((1, 7), 3)
p.d25 = ((5, 7), 3)
p.d27 = ((9, 7), 3)
p.d29 = ((3, 8), 2)
p.d31 = ((7, 8), 2)

# Across.
p.add(p.a1 == p.a24 - p.d1)
p.add(p.a3 * 3 == p.a28)
p.add(p.a6 == p.a14 * p.d31)
p.add(p.a8 == p.d20 * p.d31)
p.add(p.a10 == p.a14 + 3)
p.add(p.a12 == p.d9 + p.a28)
p.add(p.a14 == p.d29 - p.d20)
p.add(p.a15 == p.a14 + p.d19)
p.add(p.a17 == p.d1 - 3)
p.add(p.a19 == p.d16 - p.a8)
p.add(p.a21 == p.a26 + p.a32)
p.add(p.a23 == p.a12 - p.d5)
p.add(p.a24 == p.d3 + p.a23)
p.add(p.a26 == p.d11 + p.d22)
p.add(p.a28 == p.d5 - p.a17)
p.add(p.a30 == p.a3 - p.d20)
p.add(p.a32 == p.a33 - p.a3)
p.add(p.a33 == p.d11 + p.d13 + p.a28)

# Down.
p.add(p.d1 == p.a10 + p.d11)
p.add(p.d2 == p.d13 - 2)
p.add(p.d3 * 3 == p.a33)
p.add(p.d4 == p.d11 - p.d31)
p.add(p.d5 == p.d2 * p.d22)
p.add(p.d7 == p.a15 * 6)
p.add(p.d9 == p.a17 + p.a23)
p.add(p.d11 == p.d2 + p.d20)
p.add(p.d13 == p.d18 - p.a17)
p.add(p.d16 == p.a33 - p.d31)
p.add(p.d18 == p.a19 - p.d2)
p.add(p.d19 == p.d4 + p.a10)
p.add(p.d20 == p.d22 - 6)
p.add(p.d21 == p.a8 + p.a10)
p.add(p.d22 == p.d19 - p.a14)
p.add(p.d23 == p.d4 * p.d31)
p.add(p.d25 == p.a21 + p.a30)
p.add(p.d27 == p.a24 + p.d25)
p.add(p.d29 == p.a26 + 5)
p.add(p.d31 * 2 == p.d20)

p.solve()
