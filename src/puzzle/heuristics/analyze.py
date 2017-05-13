from data import meta
from puzzle.problems import anagram_problem, crossword_problem

_PROBLEM_TYPES = set()


def identify(lines):
  scores = meta.Meta()
  for t in _PROBLEM_TYPES:
    score = t.score(lines)
    if score:
      scores[t] = score
  return scores


def identify_problems(lines):
  results = []
  acc = []
  for line in lines:
    acc.append(line)
    identified = identify(acc)
    if identified and identified.magnitude() > 0:
      results.append((identified, acc))
      # Make a new accumulator; last was given to results.
      acc = []
  return results


def init():
  if _PROBLEM_TYPES:
    return
  register(anagram_problem.AnagramProblem)
  register(crossword_problem.CrosswordProblem)


def reset():
  _PROBLEM_TYPES.clear()


def problem_types():
  return _PROBLEM_TYPES


def register(cls):
  _PROBLEM_TYPES.add(cls)
