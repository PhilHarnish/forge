import sre_constants
import sre_parse
from typing import Any, Callable, List, Optional, Tuple

from data.graph import bloom_mask, bloom_node

_LOWER_ALPHA = 'abcdefghijklmnopqrstuvwxyz'
_UPPER_ALPHA = _LOWER_ALPHA.upper()
_TRANSFORMER_CACHE = {}


def transform(expression: str) -> sre_parse.SubPattern:
  parsed = sre_parse.parse(expression)
  parsed.data = _transform(parsed.data)
  return parsed

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
    parsed = transform(expression)
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
    exit_node = bloom_node.BloomNode()
    exit_node.distance(0)
    exit_node.weight(self._weight, True)
    return self._visit(exit_node, self._data, [])

  def _visit(
      self,
      cursor: bloom_node.BloomNode,
      data: list,
      exits: list) -> bloom_node.BloomNode:
    for kind, value in reversed(data):
      fn_name = '_visit_%s' % str(kind).lower()
      if not hasattr(self, fn_name):
        raise NotImplementedError('Unsupported re type %s' % kind)
      visit_fn = getattr(self, fn_name)
      exits.append(('EXIT_%s' % kind, cursor, []))
      cursor = visit_fn(cursor, value, exits)
    return cursor

  def _visit_anagram(
      self,
      cursor: bloom_node.BloomNode,
      value: list,
      exits: list) -> bloom_node.BloomNode:
    del exits
    if len(value) == 1:
      # Convert {abc} shorthand to {a,b,c}.
      groups = [[item] for item in value[0]]
    else:
      groups = value
    # Try simple anagram first.
    result = []
    for group in groups:
      value = visit_values(group)
      if not all(c.isalpha() or c == ' ' for c in value):
        break
      result.append(value)
    else:
      return cursor / result
    # Fallback to anagram of BloomNode transforms.
    result.clear()
    for group in groups:
      result.append(self._make_regex_anagram_factory(group))
    return cursor // result

  def _visit_any(
      self,
      cursor: bloom_node.BloomNode,
      value: list,
      exits: list) -> bloom_node.BloomNode:
    del exits
    assert value is None
    next_cursor = bloom_node.BloomNode()
    next_cursor.links(self._any, cursor)
    return next_cursor

  def _visit_in(
      self,
      cursor: bloom_node.BloomNode,
      value: list,
      exits: list) -> bloom_node.BloomNode:
    """Character group."""
    del self
    del exits
    edges = []
    next_cursor = bloom_node.BloomNode()
    for token in value:
      character = _visit_value(token)
      if character in bloom_mask.SEPARATOR:
        next_cursor.distance(0)
      edges.append(character)
    next_cursor.links(set(edges), cursor)
    return next_cursor

  def _visit_literal(
      self,
      cursor: bloom_node.BloomNode,
      value: int,
      exits: list) -> bloom_node.BloomNode:
    del exits
    character = _visit_value_literal(value)
    next_cursor = bloom_node.BloomNode()
    next_cursor.link(character, cursor)
    if character in bloom_mask.SEPARATOR:
      next_cursor.distance(0)
      next_cursor.weight(self._weight, False)
    return next_cursor

  def _visit_max_repeat(
      self,
      cursor: bloom_node.BloomNode,
      value: list,
      exits: list) -> bloom_node.BloomNode:
    start, end, pattern = value
    if end == sre_constants.MAXREPEAT:
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

  def _visit_subpattern(
      self,
      cursor: bloom_node.BloomNode,
      value: list,
      exits: list) -> bloom_node.BloomNode:
    group_id, x, y, pattern = value
    assert x == 0
    assert y == 0
    exit_node = cursor
    group_name = self._inverted_groups.get(group_id, group_id)
    exit_node.annotations({'EXIT_%s' % group_name: group_id})
    enter = self._visit(cursor, pattern, exits[-1][-1])
    enter.annotations({'ENTER_%s' % group_name: group_id})
    return enter

  def _make_regex_anagram_factory(
      self, data: List[tuple]) -> Callable[
          [bloom_node.BloomNode], bloom_node.BloomNode]:
    key = hash(tuple(data))
    if key not in _TRANSFORMER_CACHE:
      def factory(cursor: bloom_node.BloomNode) -> bloom_node.BloomNode:
        return self._visit(cursor, data, [])
      _TRANSFORMER_CACHE[key] = Transformer(visit_values(data), factory)

    return _TRANSFORMER_CACHE[key]


def _transform(data: list):
  transformed = []
  anagram_groups = []
  for datum in data:
    kind, value = datum
    if kind == sre_constants.LITERAL:
      # Look for {ab,c} anagram syntax.
      value = chr(value)
    elif not anagram_groups:
      transformed.append(datum)
      continue
    else:
      value = None
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


class Transformer(object):
  def __init__(
      self,
      name: str,
      fn: Callable[[bloom_node.BloomNode], bloom_node.BloomNode]) -> None:
    self._name = name
    self._fn = fn

  def __call__(self, node: bloom_node.BloomNode) -> bloom_node.BloomNode:
    return self._fn(node)

  def __str__(self) -> str:
    return self._name

  __repr__ = __str__


def visit_values(data: list) -> str:
  return ''.join(_visit_value(token) for token in data)


def _visit_value(token: tuple) -> Any:
  kind, value = token
  fn_name = '_visit_value_%s' % str(kind).lower()
  if fn_name not in globals():
    raise NotImplementedError('Unsupported re value type %s' % kind)
  return globals()[fn_name](value)


def _visit_value_anagram(value: list) -> str:
  groups = [visit_values(group) for group in value]
  if len(groups) == 1:
    return '{%s}' % ''.join(groups)
  return '{%s}' % ','.join(groups)


def _visit_value_any(value: None) -> str:
  del value
  return '.'


def _visit_value_in(data: list) -> str:
  return '[%s]' % visit_values(data)


def _visit_value_literal(value: int) -> str:
  return chr(value)


def _visit_value_max_repeat(value: Tuple[int, int, list]) -> str:
  start, end, subpattern_data = value
  subpattern_value = visit_values(subpattern_data)
  if start == 0 and end == 1:
    return '%s?' % subpattern_value
  return '%s{%s,%s}' % (subpattern_value, start, end)


def _visit_value_subpattern(value: int) -> str:
  group_id, x, y, subpattern_data = value
  return '(%s)' % visit_values(subpattern_data)
