import re
from typing import Optional

from data.graph import bloom_mask, bloom_node

_SIMPLE = re.compile(r'[a-z\.]+')
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
  if expression.islower():
    full_alpha = _LOWER_ALPHA
  else:
    full_alpha = _LOWER_ALPHA + _UPPER_ALPHA
  # Setup the "goal" state.
  cursor = bloom_node.BloomNode()
  base_require_mask = 0
  base_provide_mask = 0
  cursor.require(base_require_mask)
  distance = 0
  cursor.distance(distance)
  cursor.weight(weight, True)
  # Start at the end of expression and work backwards.
  for c in expression[::-1]:
    if c == '.':
      edges = full_alpha
    else:
      edges = c
    # Create new cursor with path to old cursor.
    next_cursor = bloom_node.BloomNode()
    distance += 1
    next_cursor.distance(distance)
    next_cursor.weight(1, False)
    # Inherit requirements from previous node.
    next_cursor.require_mask = base_require_mask
    next_cursor.provide_mask = base_provide_mask
    # Calculate edges.
    for edge in edges:
      # All edges lead to "cursor".
      next_cursor.link(edge, cursor)
      # Update require & provides for the new node.
      next_cursor.require(bloom_mask.for_alpha(edge))
    # Remember requirements from this node.
    base_require_mask = next_cursor.require_mask
    base_provide_mask = next_cursor.provide_mask
    cursor = next_cursor
  return cursor
