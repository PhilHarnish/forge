import ast

import astor

from data.logic import _grammar_transformer
from spec.mamba import *


def to_source(root):
  return astor.to_source(root, '  ')


def goal(program):
  cleaned = textwrap.dedent(program.strip('\n'))
  return to_source(ast.parse(cleaned))


with description('_GrammarTransformer'):
  with it('preserves comments as string literls'):
    program = """
      # Example with comments.
    """
    node = _grammar_transformer.transform(program)
    expected = goal("""
        '# Example with comments.'
    """)
    assignment = node.body[-1]
    expect(assignment).to(be_a(ast.Expr))
    expect(to_source(assignment)).to(look_like(expected))

  with description('visit_Module'):
    with it('prepends header'):
      node = _grammar_transformer.transform('')
      expect(node.body).to(have_len(3))

  with description('dimension definitions'):
    with it('detects dimension = a, b, c'):
      node = _grammar_transformer.transform('name <= {a, b, c}')
      expected = goal("""
          a, b, c = name = dimensions(name=['a', 'b', 'c'])
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension = 1, 2, 3'):
      node = _grammar_transformer.transform('name <= {1, 2, 3}')
      expected = goal("""
          _1, _2, _3 = name = dimensions(name=[1, 2, 3])
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension = "a", "b c", "d e f"'):
      node = _grammar_transformer.transform('name <= {"a", "b c", "d e f"}')
      expected = goal("""
          a, b_c, d_e_f = name = dimensions(name=['a', 'b c', 'd e f'])
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('registers dimension references'):
      transformer = _grammar_transformer._GrammarTransformer()
      parsed = ast.parse('name <= {1, Ex, "Multi Word"}')
      transformer.visit(parsed)
      actual = {}
      for reference, node in transformer._references.items():
        expect(node).to(be_a(ast.Name))
        actual[reference] = node.id
      expect(actual).to(equal({
        'name': 'name',
        '_1': '_1',
        'Ex': 'Ex',
        'Multi Word': 'Multi_Word',
        'Multi_Word': 'Multi_Word',
        'MultiWord': 'Multi_Word'
      }))

  with description('model constraints'):
    with it('constrains A == B'):
      node = _grammar_transformer.transform('A == B')
      expected = goal("""
          model(A == B)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('constrains A or B or C or D'):
      node = _grammar_transformer.transform('A or B or C or D')
      expected = goal("""
          model(A ^ B ^ C ^ D)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('constrains A and B and C and D'):
      node = _grammar_transformer.transform('A and B and C and D')
      expected = goal("""
          model(A & B & C & D)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('constrains A & B'):
      node = _grammar_transformer.transform('A & B')
      expected = goal("""
          model(A & B)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

  with description('reference aliases'):
    with it('no-op for well-defined references'):
      node = _grammar_transformer.transform("""
        name <= {andy, bob, cynthia}
        color <= {red, green, blue}
        andy == red
      """)
      expected = goal("""
          model(andy == red)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('rewrites string references'):
      node = _grammar_transformer.transform("""
        name <= {andy, bob, cynthia}
        color <= {red, green, 'sky blue'}
        andy == 'sky blue' & bob != sky_blue
      """)
      expected = goal("""
          model(andy == sky_blue & bob != sky_blue)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))
