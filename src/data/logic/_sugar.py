import ast

from data.logic import _ast_factory


class _AccumulatingCall(ast.Call, _ast_factory.AccumulatingExpressionMixin):
  pass


# Cloak as an "Expr" object to blend in with AST libraries.
_AccumulatingCall.__name__ = 'Call'


def sugar_abs(value):
  if not isinstance(value, ast.AST):
    return abs(value)
  return _AccumulatingCall(
      func=ast.Name(
          id='Abs',
          ctx=ast.Load(),
      ),
      args=[value],
      keywords=[],
  )


def sugar_all(iterable):
  args = ast.List(
      elts=list(iterable),
      ctx=ast.Load(),
  )
  return _AccumulatingCall(
      func=ast.Name(
          id='Conjunction',
          ctx=ast.Load(),
      ),
      args=[args],
      keywords=[],
  )


def sugar_any(iterable):
  args = ast.List(
      elts=list(iterable),
      ctx=ast.Load(),
  )
  return _AccumulatingCall(
      func=ast.Name(
          id='Disjunction',
          ctx=ast.Load(),
      ),
      args=[args],
      keywords=[],
  )


def sugar_sum(iterable):
  args = ast.List(
      elts=list(iterable),
      ctx=ast.Load(),
  )
  return _AccumulatingCall(
      func=ast.Name(
          id='Sum',
          ctx=ast.Load(),
      ),
      args=[args],
      keywords=[],
  )
