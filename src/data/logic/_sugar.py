import ast

import Numberjack

from data.logic import _ast_factory


class _AccumulatingCall(ast.Call, _ast_factory.AccumulatingExpressionMixin):
  pass


# Cloak as an "Expr" object to blend in with AST libraries.
_AccumulatingCall.__name__ = 'Call'


class Variable(ast.NameConstant, _ast_factory.AccumulatingExpressionMixin):
  """Overloads operators and accumulate expressions at runtime."""

  def __init__(self, *args):
    super(Variable, self).__init__(value=Numberjack.Variable(*args))


# Cloak as an "NameConstant" object to blend in with AST libraries.
Variable.__name__ = 'NameConstant'


def wrapped_call(fn):
  def wrapper(*args, **kwargs):
    args = [_ast_factory.coerce_value(arg) for arg in args]
    keywords = []
    for k, v in kwargs.items():
      keywords.append(ast.keyword(arg=k, value=_ast_factory.coerce_value(v)))
    return _AccumulatingCall(
        func=fn,  # This is a function pointer and normally illegal.
        args=args,
        keywords=keywords,
    )
  return wrapper


def deferred_call(fn):
  def deferred_fn(*args, **kwargs):
    def final_call():
      return fn(*args, **kwargs)
    return final_call

  return wrapped_call(deferred_fn)


class _Init(object):
  """Implements `with setup:` syntactic sugar in DSL."""

  def __enter__(self):
    pass

  def __exit__(self, exc_type, exc_val, exc_tb):
    pass

init = _Init()


def _normalize_gcc_constraints(constraints):
  cardinality_map = {}
  if isinstance(constraints, (list, set, tuple)):
    for i in constraints:
      cardinality_map[i] = (1, 1)
  elif isinstance(constraints, dict):
    for k, v in constraints.items():
      if isinstance(v, tuple):
        cardinality_map[k] = v
      elif isinstance(v, range):
        cardinality_map[k] = (getattr(v, 'start'), getattr(v, 'stop'))
      else:
        cardinality_map[k] = (v, v)
  else:
    raise TypeError('Invalid constraints for gcc: %s' % constraints)
  return cardinality_map

def gcc(vars, constraints):
  return Numberjack.Gcc(vars, _normalize_gcc_constraints(constraints))
