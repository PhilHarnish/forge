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
      expect(assignment).to(be_a(ast.Assign))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension = 1, 2, 3'):
      node = _grammar_transformer.transform('name <= {1, 2, 3}')
      expected = goal("""
          _1, _2, _3 = name = dimensions(name=[1, 2, 3])
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Assign))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension = "a", "b c", "d e f"'):
      node = _grammar_transformer.transform('name <= {"a", "b c", "d e f"}')
      expected = goal("""
          a, b_c, d_e_f = name = dimensions(name=['a', 'b c', 'd e f'])
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Assign))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension using "in" keyword'):
      node = _grammar_transformer.transform('name in {a, b, c}')
      expected = goal("""
          a, b, c = name = dimensions(name=['a', 'b', 'c'])
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Assign))
      expect(to_source(assignment)).to(look_like(expected))

    with it('supports *N repeats as shorthand'):
      node = _grammar_transformer.transform('name in {a, b, c*3}')
      expected = goal("""
          a, b, c, c, c = name = dimensions(name=['a', 'b', 'c', 'c', 'c'])
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Assign))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension created from networkx graphs'):
      node = _grammar_transformer.transform("""
        import networkx
        position in networkx.icosahedral_graph()
      """)
      expected = goal("""
          position = dimensions(position=networkx.icosahedral_graph())
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Assign))
      expect(to_source(assignment)).to(look_like(expected))

    with it('detects dimension created from other calls'):
      node = _grammar_transformer.transform("""
        position in range(26)
      """)
      expected = goal("""
          position = dimensions(position=range(26))
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Assign))
      expect(to_source(assignment)).to(look_like(expected))

    with it('compiles dimensions'):
      node = _grammar_transformer.transform('name <= {1, Ex, "Multi Word"}')
      expect(calling(compile, node, '<string>', 'exec')).not_to(raise_error)

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
        'ex': 'ex',
        'multi_word': 'multi_word'
      }))

  with description('rewrite'):
    with it('free tuples into multi-line expressions'):
      node = _grammar_transformer.transform('A, B, C')
      expected = goal("""
          A
          B
          C
      """)
      node.body = node.body[-3:]
      expect(to_source(node)).to(look_like(expected))

    with it('multi-variable comparisons into pairwise comparisons'):
      node = _grammar_transformer.transform('A > B > C')
      expected = goal("""
          model(A > B)
          model(B > C)
      """)
      node.body = node.body[-2:]
      expect(to_source(node)).to(look_like(expected))

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

    with it('constrains simple function calls'):
      node = _grammar_transformer.transform('abs(A - B)')
      expected = goal("""
          model(abs(A - B))
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('constrains complex function calls'):
      node = _grammar_transformer.transform('any([A, B])')
      expected = goal("""
          model(any([A, B]))
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('constrains for loop body'):
      node = _grammar_transformer.transform("""
        for a in range(5):
          a < b
      """)
      expected = goal("""
        for a in range(5):
          model(a < b)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.For))
      expect(to_source(assignment)).to(look_like(expected))

  with description('if'):
    with it('converts if->then statements'):
      node = _grammar_transformer.transform('if A: B')
      expected = goal("""
        if "A":
          model(A <= B)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.If))
      expect(to_source(assignment)).to(look_like(expected))

    with it('converts if->then/else statements'):
      node = _grammar_transformer.transform("""
        if A:
          B
        else:
          C
      """)
      expected = goal("""
        if "A":
          model(A <= B)
          model(A + C >= 1)
      """)
      result = node.body[-1]
      expect(result).to(be_a(ast.If))
      expect(to_source(result)).to(look_like(expected))

    with it('converts if->then/else statements with longer bodies'):
      node = _grammar_transformer.transform("""
        if A:
          B1
          B2
        else:
          C1
          C2
      """)
      expected = goal("""
        if "A":
          model(A <= B1 & B2)
          model(A + (C1 & C2) >= 1)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.If))
      expect(to_source(assignment)).to(look_like(expected))

    with it('supports if/else assignments'):
      node = _grammar_transformer.transform("""
        if A:
          x = 1
        else:
          x = 2
      """)
      expected = goal("""
        if "A":
          x = (A == True) * 1 + (A == False) * 2
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.If))
      expect(to_source(assignment)).to(look_like(expected))

    with it('supports if/else mixed condition and assignments'):
      node = _grammar_transformer.transform("""
        if A:
          A > B
          x = 1
        else:
          x = 2
      """)
      expected = goal("""
        if "A":
          x = (A == True) * 1 + (A == False) * 2
          model(A <= (A > B))
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.If))
      expect(to_source(assignment)).to(look_like(expected))

    with it('supports nested if statements'):
      node = _grammar_transformer.transform("""
        if A:
          if B:
            if C:
              x == 3
            else:
              x == 2
          else:
            x == 1
        else:
          x == 0
      """)
      expected = goal("""
        if 'A':
          model(A <= (B <= (C <= (x == 3)) & (C + (x == 2) >= 1)) & (B + (x == 1) >= 1)
              )
          model(A + (x == 0) >= 1)
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.If))
      expect(to_source(assignment)).to(look_like(expected))

    with it('supports if statements in generators'):
      node = _grammar_transformer.transform("""
        all(implication[i] for i in range(10) if condition) 
      """)
      expected = goal("""
        model(all(condition <= implication[i] for i in range(10)))
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
        andy == 'sky blue' and bob != sky_blue
      """)
      expected = goal("""
          model((andy == sky_blue) & (bob != sky_blue))
      """)
      assignment = node.body[-1]
      expect(assignment).to(be_a(ast.Expr))
      expect(to_source(assignment)).to(look_like(expected))

    with it('matches alias references'):
      node = _grammar_transformer.transform("""
        key <= {'space case', 'kebab-case', snake_case, CamelCase}
        'space case' != 'kebab-case' != 'snake_case' != 'CamelCase'
      """)
      expected = goal("""
        model(space_case != kebab_case)
        model(kebab_case != snake_case)
        model(snake_case != camelcase)
      """)
      node.body = node.body[-3:]
      expect(to_source(node)).to(look_like(expected))
