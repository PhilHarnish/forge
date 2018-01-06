import re
import sre_parse
from typing import Any, Optional

from data.graph import bloom_mask, bloom_node

_SIMPLE = re.compile(r'[a-zA-Z. ]+')
_LOWER_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
_UPPER_ALPHA = _LOWER_ALPHA.upper()

def parse(expression: str, weight: Optional[float] = 1) -> bloom_node.BloomNode:
  match = re.match(_SIMPLE, expression)
  if not match or match.span(0)[1] != len(expression):
    visitor = _RegexVisitor(expression, weight)
    return visitor.visit(sre_parse.parse(expression))
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


class _RegexVisitor(object):
  def __init__(self, expression: str, weight: float):
    self._expression = expression
    self._weight = weight

  def visit(self, data: list) -> bloom_node.BloomNode:
    goal = bloom_node.BloomNode()
    goal.distance(0)
    goal.weight(self._weight, True)
    return self._visit(goal, data)

  def _visit(
      self, cursor: bloom_node.BloomNode, data: list) -> bloom_node.BloomNode:
    for kind, value in reversed(data):
      fn_name = '_visit_%s' % kind
      if not hasattr(self, fn_name):
        raise NotImplementedError('Unsupported re type %s' % kind)
      visit_fn = getattr(self, fn_name)
      cursor = visit_fn(cursor, value)
    return cursor

  def _visit_IN(
      self, cursor: bloom_node.BloomNode, data: list) -> bloom_node.BloomNode:
    """Character group."""
    edges = []
    next_cursor = bloom_node.BloomNode()
    for datum in data:
      value = self._visit_value(datum)
      if value in bloom_mask.SEPARATOR:
        next_cursor.distance(0)
      edges.append(value)
    next_cursor.links(''.join(set(edges)), cursor)
    return next_cursor

  def _visit_LITERAL(
      self, cursor: bloom_node.BloomNode, data: int) -> bloom_node.BloomNode:
    value = self._visit_value_LITERAL(data)
    next_cursor = bloom_node.BloomNode()
    next_cursor.link(value, cursor)
    if value in bloom_mask.SEPARATOR:
      next_cursor.distance(0)
      next_cursor.weight(self._weight, False)
    return next_cursor

  def _visit_MAX_REPEAT(
      self, cursor: bloom_node.BloomNode, data: list) -> bloom_node.BloomNode:
    start, end, pattern = data
    if str(end) == 'MAXREPEAT':
      raise NotImplementedError('Unable to repeat MAXREPEAT')
    chain_start = cursor
    exits = []
    if start == 0:
      # Path to cursor is possible either via chain or original cursor.
      exits.append(cursor)
      link_count = end - 1
    else:
      link_count = end - start
    for _ in range(link_count + 1):
      chain_start = self._visit(chain_start, pattern)
      # Path may go through this chain.
      exits.append(chain_start)
    result = exits[0]
    for exit in exits[1:]:
      result += exit
    return result

  def _visit_value(self, data: tuple) -> Any:
    kind, value = data
    fn_name = '_visit_value_%s' % kind
    if not hasattr(self, fn_name):
      raise NotImplementedError('Unsupported re type %s' % kind)
    return getattr(self, fn_name)(value)

  def _visit_value_LITERAL(self, data: int) -> str:
    return chr(data)
