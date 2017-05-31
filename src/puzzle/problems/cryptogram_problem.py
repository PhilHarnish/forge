from puzzle.problems import problem


class CryptogramProblem(problem.Problem):
  @staticmethod
  def score(lines):
    if lines and lines[0]:
      return 0.1
    return 0

  def _solve(self):
    return {}
