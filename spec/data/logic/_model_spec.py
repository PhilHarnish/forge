from data.logic import _model
from spec.mamba import *

with description('_model._Model'):
  with description('constructor'):
    with it('handles simple input'):
      expect(calling(_model._Model, None)).not_to(raise_error)

  with description('constraints'):
    with before.each:
      self.subject = _model._Model(None)

    with it('accumulates constraints'):
      self.subject(1, 2, 3)
      expect(self.subject.constraints()).to(have_len(3))
