from data import meta
from puzzle.problems import acrostic_problem, anagram_problem, \
  number_problem
from puzzle.problems.crossword import crossword_problem, cryptic_problem

_PROBLEM_TYPES = set()
_IDENTIFY_ORDER = []


def identify(lines, hint=None):
  scores = meta.Meta()
  for group in _IDENTIFY_ORDER:
    group_count = 0
    group_scale = 2 * len(group)
    for t in group:
      score = t.score(lines)
      if score:
        # For group size of 5: 1, .9, .8, .7, .6, .5.
        penalty_multiplier = 1 - (group_count / group_scale)
        if hint is None:
          pass
        elif isinstance(hint, str):
          if hint.lower() not in t.__name__.lower():
            penalty_multiplier *= .25
        elif isinstance(hint, type):
          if t != hint:
            penalty_multiplier *= .25
        scores[t] = score * penalty_multiplier
        if score == 1:
          group_count += 1
  return scores


def identify_problems(lines, hint=None):
  if len(lines) > 1:
    # Try to parse the entire thing at once first.
    identified = identify(lines, hint=hint)
    if identified and identified.magnitude() == 1:
      return [(identified, lines)]
  results = []
  for line in lines:
    identified = identify([line], hint=hint)
    if identified and identified.magnitude() > 0:
      results.append((identified, [line]))
  return sorted(results, key=lambda x: x[0].magnitude(), reverse=True)


def init():
  if _PROBLEM_TYPES:
    return
  register(acrostic_problem.AcrosticProblem)
  register(anagram_problem.AnagramProblem)
  register(cryptic_problem.CrypticProblem, crossword_problem.CrosswordProblem)
  register(number_problem.NumberProblem)


def reset():
  _PROBLEM_TYPES.clear()
  _IDENTIFY_ORDER.clear()


def problem_types():
  return _PROBLEM_TYPES


def register(*problems):
  for problem in problems:
    if problem in _PROBLEM_TYPES:
      raise IndexError('%s already registered' % problem)
    _PROBLEM_TYPES.add(problem)
  _IDENTIFY_ORDER.append(problems)
