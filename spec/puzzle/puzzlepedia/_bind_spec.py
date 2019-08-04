from puzzle.puzzlepedia import _bind
from spec.mamba import *

with description('_bind'):
  with description('callback_without_event'):
    with it('returns a callable function'):
      expect(_bind.callback_without_event(lambda: None)).to(be_callable)

    with it('returns a partial over inputs'):
      stub = mock.Mock()
      _bind.callback_without_event(stub, 1, 2, 3)(None)
      expect(stub).to(have_been_called_with(1, 2, 3))
