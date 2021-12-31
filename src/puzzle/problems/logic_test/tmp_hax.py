from typing import List

from puzzle.problems.logic_test import _parse, _solve


def parse_questions(text: str) -> List[_parse.Question]:
  return _parse.parse_questions(text)


def parse_option(text: str) -> str:
  return str(_parse.parse_option('A', text))


def solve(text: str) -> List:
  solutions = []
  for question in parse_questions(text):
    solutions.append(_solve.solve(question))
  return solutions
