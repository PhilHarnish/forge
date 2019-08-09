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

  with description('computation'):
    with before.each:
      self.img = image.Image(np.zeros((3, 3), dtype=np.uint8))
      self.bincount_patch = mock.patch(
          'data.image.image.np.bincount', return_value='patched')
      self.mock_bincount = self.bincount_patch.start()

    with after.each:
      self.bincount_patch.stop()

    with it('caches computations'):
      expect(self.mock_bincount).not_to(have_been_called)
      expect(self.img.bincount).to(equal('patched'))
      expect(self.mock_bincount).to(have_been_called_once)
      expect(self.img.bincount).to(equal('patched'))
      expect(self.mock_bincount).to(have_been_called_once)

    with it('invalidates computations'):
      expect(self.img.bincount).to(equal('patched'))
      expect(self.mock_bincount).to(have_been_called_once)
      self.img.invert()
      expect(self.img.bincount).to(equal('patched'))
      expect(self.mock_bincount).to(have_been_called_times(2))

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

  with it('get_debug_data'):
    data = np.ones((3, 3), dtype=np.uint8)
    expect(image.Image(data).get_debug_data()).to(be(data))
