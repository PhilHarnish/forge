import re
from typing import Optional

from data.graph import bloom_mask, bloom_node

_SIMPLE = re.compile(r'[a-zA-Z. ]+')
_LOWER_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
_UPPER_ALPHA = _LOWER_ALPHA.upper()

def parse(expression: str, weight: Optional[float] = 1) -> bloom_node.BloomNode:
  match = re.match(_SIMPLE, expression)
  if not match or match.span(0)[1] != len(expression):
    raise NotImplementedError('Unsupported characters in %s ("%s")' % (
      expression, re.sub(_SIMPLE, '', expression)
    ))
  return _to_simple_nodes(normalize(expression), weight)

def normalize(expression: str) -> str:
  if expression.isupper() and not expression.islower():
    # Convert an ALL CAPS expression to lower case.
    return expression.lower()
  return expression

def _to_simple_nodes(expression: str, weight) -> bloom_node.BloomNode:
  if not expression.islower() and any(c.isupper() for c in expression):
    full_alpha = _LOWER_ALPHA + _UPPER_ALPHA
  else:
    full_alpha = _LOWER_ALPHA
  # Setup the "goal" state.
  cursor = bloom_node.BloomNode()
  cursor.distance(0)
  cursor.weight(weight, True)
  # Start at the end of expression and work backwards.
  for c in expression[::-1]:
    if c == '.':
      edges = full_alpha
    else:
      edges = c
    # Create new cursor with path to old cursor.
    next_cursor = bloom_node.BloomNode()
    if c in bloom_mask.SEPARATOR:
      next_cursor.distance(0)
      next_cursor.weight(weight, False)
    next_cursor.links(edges, cursor)
    cursor = next_cursor
  return cursor
