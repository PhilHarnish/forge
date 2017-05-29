from data import meta
from puzzle.problems import acrostic_problem, anagram_problem, \
  number_problem
from puzzle.problems.crossword import crossword_problem, cryptic_problem

_PROBLEM_TYPES = set()


def identify(lines):
  scores = meta.Meta()
  for t in _PROBLEM_TYPES:
    score = t.score(lines)
    if score:
      scores[t] = score
  return scores


def identify_problems(lines):
  if len(lines) > 1:
    # Try to parse the entire thing at once first.
    identified = identify(lines)
    if identified and identified.magnitude() == 1:
      return [(identified, lines)]
  results = []
  for line in lines:
    identified = identify([line])
    if identified and identified.magnitude() > 0:
      results.append((identified, [line]))
  return sorted(results, key=lambda x: x[0].magnitude(), reverse=True)


def init():
  if _PROBLEM_TYPES:
    return
  register(acrostic_problem.AcrosticProblem)
  register(anagram_problem.AnagramProblem)
  register(crossword_problem.CrosswordProblem)
  register(cryptic_problem.CrypticProblem)
  register(number_problem.NumberProblem)


def reset():
  _PROBLEM_TYPES.clear()


def problem_types():
  return _PROBLEM_TYPES


def register(cls):
  _PROBLEM_TYPES.add(cls)
