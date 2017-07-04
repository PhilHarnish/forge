import ast

import astor

from data.logic import _grammar_transformer
from spec.mamba import *


def transform(program):
  return parse(program), _grammar_transformer._GrammarTransformer(program)


def parse(program):
  cleaned = textwrap.dedent(program.strip('\n'))
  return ast.parse(cleaned)


def to_source(root):
  return astor.to_source(root, '  ')


def goal(program):
  return to_source(parse(program))


with description('_GrammarTransformer'):
  with description('visit_Module'):
    with it('prepends header'):
      node, transformer = transform('')
      transformer.visit(node)
      expect(node.body).to(have_len(3))

  with description('visit_Assign'):
    with it('detects dimension = a, b, c'):
      node, transformer = transform('name <= {a, b, c}')
      expected = goal("""
          a, b, c = name = dimensions(name=['a', 'b', 'c'])
      """)
      transformer.visit(node)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension = 1, 2, 3'):
      node, transformer = transform('name <= {1, 2, 3}')
      expected = goal("""
          _1, _2, _3 = name = dimensions(name=[1, 2, 3])
      """)
      transformer.visit(node)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension = "a", "b c", "d e f"'):
      node, transformer = transform('name <= {"a", "b c", "d e f"}')
      expected = goal("""
          a, b_c, d_e_f = name = dimensions(name=['a', 'b c', 'd e f'])
      """)
      transformer.visit(node)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))
