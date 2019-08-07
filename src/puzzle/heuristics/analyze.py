import collections
from typing import List, Optional, Set, Tuple, Type, Union

import numpy as np

from data import meta
from puzzle.problems import acrostic_problem, anagram_problem, \
  cryptogram_problem, logic_problem, morse_problem, \
  number_problem, problem, solved_problem
from puzzle.problems.crossword import crossword_problem, cryptic_problem
from puzzle.problems.image import image_problem

Hint = Optional[Union[str, type]]


_PROBLEM_TYPES = set()
_IDENTIFY_ORDER = collections.defaultdict(list)


def identify(
    data: problem.ProblemData, hint: Hint = None) -> meta.Meta[problem.Problem]:
  scores = meta.Meta()
  try:
    matched_type = type(next(iter(data)))
  except StopIteration:
    matched_type = str
  if matched_type not in _IDENTIFY_ORDER:
    raise NotImplementedError('Unable to identify type %s' % matched_type)
  for group in _IDENTIFY_ORDER[matched_type]:
    group_count = 0
    group_scale = 2 * len(group)
    for t in group:
      score = t.score(data)
      if score:
        # For group size of 5: 1, .9, .8, .7, .6, .5.
        penalty_multiplier = 1 - (group_count / group_scale)
        if hint is None:
          pass
        elif t == solved_problem.SolvedProblem:
          pass
        elif isinstance(hint, str):
          hint = hint.lower()
          type_name = t.__name__.lower()
          if hint not in type_name:
            penalty_multiplier *= .25
          elif type_name.startswith(hint):  # Perfect match.
            penalty_multiplier = 1
            score = 1
        elif isinstance(hint, type):
          if t == hint:  # Perfect match.
            penalty_multiplier = 1
            score = 1
          else:
            penalty_multiplier *= .25
        scores[t] = score * penalty_multiplier
        if score == 1:
          group_count += 1
  return scores


def identify_problems(
    lines: problem.ProblemData, hint: Hint = None
) -> List[Tuple[meta.Meta, problem.ProblemData]]:
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
  return results


def init() -> None:
  if _PROBLEM_TYPES:
    return
  register(solved_problem.SolvedProblem)
  register(acrostic_problem.AcrosticProblem)
  register(anagram_problem.AnagramProblem)
  register(cryptic_problem.CrypticProblem, crossword_problem.CrosswordProblem)
  register(cryptogram_problem.CryptogramProblem)
  register(logic_problem.LogicProblem)
  register(morse_problem.MorseProblem)
  register(number_problem.NumberProblem)
  # Generic image problem will be replaced with more specific matchers later.
  register(image_problem.ImageProblem, match_type=np.ndarray)


def reset() -> None:
  _PROBLEM_TYPES.clear()
  _IDENTIFY_ORDER.clear()


def problem_types() -> Set[Type[problem.Problem]]:
  return _PROBLEM_TYPES


def register(
    *problems: Type[problem.Problem],
    match_type: Type = str) -> None:
  for p in problems:
    if p in _PROBLEM_TYPES:
      raise IndexError('%s already registered' % p)
    _PROBLEM_TYPES.add(p)
  _IDENTIFY_ORDER[match_type].append(problems)
