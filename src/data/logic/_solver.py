class Solver(object):
  def __init__(self, model, solver, deferred):
    self._model = model
    self._solver = solver
    self._solved = False
    self._deferred = deferred

  def solve(self):
    solution_found = False
    if not self._solved:
      self._solved = True
      solution_found = self._solver.solve()
    elif not self._solver.is_unsat():
      solution_found = bool(self._solver.getNextSolution())
    if solution_found:
      self._process_deferred()
    return solution_found

  def solved(self):
    return self._solved and self._solver.is_sat() or not self._solver.is_unsat()

  def __str__(self):
    if not self._solved:
      return '<unsolved>'
    headers, cells = self._model.get_solutions()
    widths = [len(s) for s in headers]
    normalized = []
    normalized.append(headers)
    for row in cells:
      normalized_row = []
      normalized.append(normalized_row)
      for index, column in enumerate(row):
        cell = ', '.join([str(c) for c in column])
        normalized_row.append(cell)
        widths[index] = max(widths[index], len(cell))
    result = []
    for row in normalized:
      result_row = []
      for index, cell in enumerate(row):
        fmt_str = '%' + str(widths[index]) + 's'
        result_row.append(fmt_str % cell)
      result.append(' | '.join(result_row))
      result.append('\n')
    return ''.join(result)

  def _process_deferred(self):
    for fn in self._deferred:
      fn()
