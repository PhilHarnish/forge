from data.wordnik import _client
from spec.mamba import *

with description('_client'):
  with description('get_client'):
    with it('executes without error'):
      expect(calling(_client.get_client)).not_to(raise_error)
