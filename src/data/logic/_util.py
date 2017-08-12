import ast
import operator

import Numberjack


def address(dimensions, constraints):
  """Returns the address for 'constraints'. Ignores unset fields."""
  address_parts = []
  for dimension in dimensions:
    if dimension in constraints:
      if constraints[dimension] is None:
        address_parts.append(dimension)
      else:
        address_parts.append('%s[%s]' % (
            dimension, repr(constraints[dimension]).replace('\'', '"')))
  return '.'.join(address_parts)


def parse(address):
  result = {}
  for subscript in address.split('.'):
    if '[' in subscript and ']' in subscript:
      key, value_str = subscript.rstrip(']').split('[')
      value = ast.literal_eval(value_str)
    else:
      key = subscript
      value = None
    result[key] = value
  return result


def combine(a, b):
  combined = a.copy()
  for key, value in b.items():
    if key not in combined or combined[key] is None:
      combined[key] = value
    elif value is None:
      pass  # combined already has a more specific version of key.
    elif combined[key] != value:
      raise KeyError('%s is over constrained (both %s and %s)' % (
        key, combined[key], value,
      ))
  return combined


_NUMBERJACK_OPERATOR_VALUE_MAP = {
  'sum': operator.add,
}


def numberjack_solution(expr):
  if isinstance(expr, (int, str, bool)):
    return expr
  elif hasattr(expr, 'is_built') and expr.is_built():
    return expr.get_value()
  elif isinstance(expr, Numberjack.Variable):
    raise ValueError('expr "%s" is not built' % expr)
  elif isinstance(expr, Numberjack.Predicate):
    val_result = list([numberjack_solution(child) for child in expr.children])
    val_op_key = expr.operator.lower()
    if val_op_key in _NUMBERJACK_OPERATOR_VALUE_MAP:
      val_op = _NUMBERJACK_OPERATOR_VALUE_MAP[val_op_key]
    else:
      val_op = getattr(operator, '__%s__' % val_op_key)
    if expr.has_parameters():
      # A - B is implemented as Sum(1*A + -1*B).
      parameters = expr.parameters[0]
    else:
      parameters = [1] * len(val_result)
    value = parameters[0] * val_result[0]
    for i, v in enumerate(val_result[1:]):
      value = val_op(value, parameters[i + 1] * v)
    return value
  else:
    raise TypeError('Unable to val/str %s' % expr)


def literal_value(node):
  """Given an AST node returns the python literal value."""
  if isinstance(node, ast.NameConstant):
    return node.value
  elif isinstance(node, ast.Str):
    return node.s
  elif isinstance(node, ast.Num):
    return node.n
  elif isinstance(node, ast.List):
    return list(literal_value(v) for v in node.elts)
  elif isinstance(node, ast.Tuple):
    return tuple(literal_value(v) for v in node.elts)
  raise TypeError('Unable to convert literal value %s' % node)
