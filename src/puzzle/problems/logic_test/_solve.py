import itertools
from typing import List

from puzzle.problems.logic_test import _parse


_PROGRAM = """
_TF = (True, False)
for env in itertools.product(*product_args):
  (%(env_expand)s) = env
  if all([
%(conditions)s
  ]):
    results.append(
      chr(ord('A') - 1 + int(''.join('01'[x] for x in reversed(env)), 2))
    )
"""



def solve(question: _parse.Question) -> List[bool]:
  variables = question.variables()
  env_expand = ', '.join(variables)
  program = _PROGRAM % {
    'env_expand': env_expand,
    'conditions': str(question).replace('  #', ',  #'),
  }
  print(program)
  return []
