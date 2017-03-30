import collections

from src.puzzle.problems import problem

def identify(src):
  scores = {}
  for t in problem.problem_types():
    score = t.score(src)
    if score:
      scores[t] = t.score(src)
  # Return sorted values, highest first.
  ordered = collections.OrderedDict()
  for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    ordered[k] = v
  return ordered
