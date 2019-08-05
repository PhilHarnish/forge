import numpy as np

from data.image import image
from spec.mamba import *

with description('image'):
  with it('constructs without error'):
    expect(calling(image.Image, np.zeros((3, 3)))).not_to(raise_error)

  with it('tracks mutations'):
    i = image.Image(np.zeros((3, 3), dtype=np.uint8))
    i.invert()
    expect(i.has_mutation('invert')).to(be_true)

  with it('tracks mutations from parents'):
    i = image.Image(np.zeros((3, 3), dtype=np.uint8))
    i2 = i.invert().fork().fork()
    expect(i2.has_mutation('invert')).to(be_true)

  with description('crop'):
    with it('requires normalize first'):
      i = image.Image(np.ones((3, 3), dtype=np.uint8))
      expect(calling(i.crop, 0)).to(raise_error(
          ValueError, 'normalize() must occur before crop(0)'))

  with description('__str__'):
    with it('handles empty mutations'):
      i = image.Image(np.ones((3, 3), dtype=np.uint8))
      expect(str(i)).to(look_like("""
        Image()
      """))

    with it('handles simple mutations'):
      i = image.Image(np.ones((3, 3), dtype=np.uint8))
      i.normalize().invert()
      expect(str(i)).to(look_like("""
        Image()
          .normalize()
          .invert()
      """))

    with it('handles mutations mutations across generations'):
      i = image.Image(np.ones((3, 3), dtype=np.uint8))
      i = i.normalize().fork().invert()
      expect(str(i)).to(look_like("""
        Image()
          .normalize()
          .fork()
          .invert()
      """))

    with it('handles just generations'):
      i = image.Image(np.ones((3, 3), dtype=np.uint8))
      i = i.fork().fork().fork()
      expect(str(i)).to(look_like("""
        Image()
          .fork()
          .fork()
          .fork()
      """))