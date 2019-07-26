from data.image import layer
from spec.mamba import *

with description('layer'):
  with description('constructor') as self:
    with it('instantiates'):
      expect(calling(layer.Layer, '', [])).not_to(raise_error)
