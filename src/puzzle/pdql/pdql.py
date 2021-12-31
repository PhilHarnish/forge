from puzzle.pdql import q, _query


def input(*args, **kwargs):
  return q.Q().input(*args, **kwargs)

def query(*args, **kwargs):
  return q.Q().query(*args, **kwargs)
