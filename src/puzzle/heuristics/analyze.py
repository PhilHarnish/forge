from src.data import meta
from src.puzzle.problems import crossword_problem


_PROBLEM_TYPES = set()


def identify(line):
  scores = meta.Meta()
  for t in _PROBLEM_TYPES:
    score = t.score(line)
    if score:
      scores[t] = t.score(line)
  return scores


def init():
  if _PROBLEM_TYPES:
    return
  register(crossword_problem.CrosswordProblem)


def reset():
  _PROBLEM_TYPES.clear()


def problem_types():
  return _PROBLEM_TYPES


def register(cls):
  _PROBLEM_TYPES.add(cls)
