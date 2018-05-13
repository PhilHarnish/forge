import collections
from typing import Dict, Iterable, List, Union

from data import types
from data.graph import bloom_node, walk as walk_internal

Expression = bloom_node.BloomNode
Expressions = Union[List[Expression], Dict[str, Expression]]
WeightedWords = Union[List[types.WeightedWord], Dict[str, types.WeightedWord]]
_EXHAUSTED = {}


class ResultSet(dict):
  def __init__(self, values: WeightedWords) -> None:
    if isinstance(values, list):
      kwargs = enumerate(values)
    else:
      kwargs = values
    super(ResultSet, self).__init__(kwargs)


class Results(object):
  def __init__(self, expressions: Expressions) -> None:
    if isinstance(expressions, list):
      expressions = collections.OrderedDict(enumerate(expressions))
    self._expressions = expressions

  def __iter__(self) -> Iterable[ResultSet]:
    if not self._expressions:
      return
    sources = [(k, walk_internal.walk(v)) for k, v in self._expressions.items()]
    values = [(k, next(v, _EXHAUSTED)) for k, v in sources]
    if not any(v is _EXHAUSTED for _, v in values):
      yield ResultSet(dict(values))


def walk(expressions: Expressions) -> Iterable[ResultSet]:
  return Results(expressions)
