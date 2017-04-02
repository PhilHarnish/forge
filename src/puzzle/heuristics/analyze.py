import collections

from src.puzzle.problems import problem
from src.puzzle.problems import crossword_problem


_PROBLEM_TYPES = set()


def identify(src):
  scores = {}
  for t in _PROBLEM_TYPES:
    score = t.score(src)
    if score:
      scores[t] = t.score(src)
  # Return sorted values, highest first.
  return collections.OrderedDict(
      sorted(scores.items(), key=lambda x: x[1], reverse=True))


def init():
  register(crossword_problem.CrosswordProblem)


def reset():
  _PROBLEM_TYPES.clear()


def problem_types():
  return _PROBLEM_TYPES


def register(cls):
  _PROBLEM_TYPES.add(cls)
