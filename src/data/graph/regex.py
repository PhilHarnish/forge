import sre_parse
from typing import Any, Optional

from data.graph import bloom_mask, bloom_node

_LOWER_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
_UPPER_ALPHA = _LOWER_ALPHA.upper()


def parse(expression: str, weight: Optional[float] = 1) -> bloom_node.BloomNode:
  expression = normalize(expression)
  visitor = _RegexVisitor(expression, weight)
  return visitor.visit()


def normalize(expression: str) -> str:
  if expression.isupper() and not expression.islower():
    # Convert an ALL CAPS expression to lower case.
    return expression.lower()
  return expression


class _RegexVisitor(object):
  def __init__(self, expression: str, weight: float):
    parsed = sre_parse.parse(expression)
    self._pattern = parsed.pattern
    self._data = parsed.data
    self._inverted_groups = {
      value: name for name, value in self._pattern.groupdict.items()
    }
    self._weight = weight
    if not expression.islower() and any(c.isupper() for c in expression):
      self._any = _LOWER_ALPHA + _UPPER_ALPHA
    else:
      self._any = _LOWER_ALPHA

  def visit(self) -> bloom_node.BloomNode:
    exit = bloom_node.BloomNode()
    exit.distance(0)
    exit.weight(self._weight, True)
    return self._visit(exit, self._data, [])

  def _visit(
      self,
      cursor: bloom_node.BloomNode,
      data: list,
      exits: list) -> bloom_node.BloomNode:
    data = self._transform(data)
    for kind, value in reversed(data):
      fn_name = '_visit_%s' % kind
      if not hasattr(self, fn_name):
        raise NotImplementedError('Unsupported re type %s' % kind)
      visit_fn = getattr(self, fn_name)
      exits.append(('EXIT_%s' % kind, cursor, []))
      cursor = visit_fn(cursor, value, exits)
    return cursor

  def _visit_ANAGRAM(
      self,
      cursor: bloom_node.BloomNode,
      data: list,
      exits: list) -> bloom_node.BloomNode:
    del data
    del exits
    # TODO: If length of list is 1 then all literals can be anagrammed.
    return cursor

  def _visit_ANY(
      self,
      cursor: bloom_node.BloomNode,
      data: list,
      exits: list) -> bloom_node.BloomNode:
    del exits
    assert data is None
    next_cursor = bloom_node.BloomNode()
    next_cursor.links(self._any, cursor)
    return next_cursor

  def _visit_IN(
      self,
      cursor: bloom_node.BloomNode,
      data: list,
      exits: list) -> bloom_node.BloomNode:
    """Character group."""
    del exits
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
      self,
      cursor: bloom_node.BloomNode,
      data: int,
      exits: list) -> bloom_node.BloomNode:
    del exits
    value = self._visit_value_LITERAL(data)
    next_cursor = bloom_node.BloomNode()
    next_cursor.link(value, cursor)
    if value in bloom_mask.SEPARATOR:
      next_cursor.distance(0)
      next_cursor.weight(self._weight, False)
    return next_cursor

  def _visit_MAX_REPEAT(
      self,
      cursor: bloom_node.BloomNode,
      data: list,
      exits: list) -> bloom_node.BloomNode:
    start, end, pattern = data
    if str(end) == 'MAXREPEAT':
      raise NotImplementedError('Unable to repeat MAXREPEAT')
    chain_start = cursor
    exit_nodes = []
    if start == 0:
      # Path to cursor is possible either via chain or original cursor.
      exit_nodes.append(cursor)
      link_count = end - 1
    else:
      link_count = end - start
    for _ in range(link_count + 1):
      chain_start = self._visit(chain_start, pattern, exits[-1][-1])
      # Path may go through this chain.
      exit_nodes.append(chain_start)
    result = exit_nodes[0]
    for exit_node in exit_nodes[1:]:
      result += exit_node
    return result

  def _visit_SUBPATTERN(
      self,
      cursor: bloom_node.BloomNode,
      data: list,
      exits: list) -> bloom_node.BloomNode:
    group_id, x, y, pattern = data
    assert x == 0
    assert y == 0
    exit = cursor
    group_name = self._inverted_groups.get(group_id, group_id)
    exit.annotations({'EXIT_%s' % group_name: group_id})
    enter = self._visit(cursor, pattern, exits[-1][-1])
    enter.annotations({'ENTER_%s' % group_name: group_id})
    return enter

  def _visit_value(self, data: tuple) -> Any:
    kind, value = data
    fn_name = '_visit_value_%s' % kind
    if not hasattr(self, fn_name):
      raise NotImplementedError('Unsupported re type %s' % kind)
    return getattr(self, fn_name)(value)

  def _visit_value_LITERAL(self, data: int) -> str:
    return chr(data)

  def _transform(self, data: list):
    transformed = []
    anagram_groups = []
    for datum in data:
      kind, value = datum
      if str(kind) != 'LITERAL':
        transformed.append(datum)
        continue
      # Look for {ab,c} anagram syntax.
      value = chr(value)
      if value == '{':
        anagram_groups.append([[]])
      elif not anagram_groups:
        transformed.append(datum)
      elif value == ',':
        anagram_groups[-1].append([])
      elif value == '}':
        transformed.append(('ANAGRAM', anagram_groups.pop()))
      else:
        anagram_groups[-1][-1].append(datum)
    return transformed
