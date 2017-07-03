import ast

from data.logic import _grammar_transformer
from spec.mamba import *

with description('_GrammarTransformer'):
  with before.all:
    self.transformer = _grammar_transformer._GrammarTransformer(
        '\n'.join('# line #%s.' % i for i in range(1, 10)))

  with description('visit_Module'):
    with it('prepends header'):
      node = ast.Module(body=[])
      result = self.transformer.visit(node)
      expect(node.body).to(have_len(3))
