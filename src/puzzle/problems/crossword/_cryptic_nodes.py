from typing import NamedTuple, List

from data import crossword


class Clue(str):
  def __init__(self, value) -> None:
    super(Clue, self).__init__(value)
    self._tokens = crossword.tokenize_clue(value)


class _Node(object):
  _clue: Clue
  _occupied: int

  def __init__(self, clue: Clue, occupied: int) -> None:
    self._clue = clue
    self._occupied = occupied


class Parsed(List):
  pass

# A list of nodes, initially Nulls
