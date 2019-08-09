from puzzle.constraints.image import prepare_image_constraints
from spec.mamba import *

with description('prepare_image_constraints') as self:
  with before.each:
    self.constraints = prepare_image_constraints.PrepareImageConstraints()

  with description('validation'):
    with it('accepts low crop value'):
      self.constraints.crop = 0
      expect(self.constraints).to(have_property('crop', 0))

    with it('accepts high crop value'):
      self.constraints.crop = 255
      expect(self.constraints).to(have_property('crop', 255))

  with description('is_modifiable'):
    with description('when assigning False'):
      with it('allows unencumbered properties'):
        expect(self.constraints.is_modifiable('enhance')).to(be_true)
        self.constraints.enhance = False
        expect(self.constraints).to(have_property('enhance', False))

      with it('forbids encumbered properties'):
        expect(self.constraints.is_modifiable('normalize')).to(be_false)

      with it('understands None and 0'):
        self.constraints.enhance = False
        self.constraints.grayscale = False
        expect(self.constraints.is_modifiable('normalize')).to(be_false)
        self.constraints.crop = None
        expect(self.constraints.is_modifiable('normalize')).to(be_true)

      with it('enforces is_modifiable result'):
        expect(calling(setattr, self.constraints, 'normalize', False)).to(
            raise_error(AttributeError, 'normalize is not modifiable'))

    with description('when assigning True'):
      with it('allows unencumbered properties'):
        self.constraints.enhance = False
        expect(self.constraints.is_modifiable('enhance')).to(be_true)
        self.constraints.enhance = True
        expect(self.constraints).to(have_property('enhance', True))

      with it('forbids encumbered properties'):
        self.constraints.enhance = False
        self.constraints.grayscale = False
        expect(self.constraints.is_modifiable('enhance')).to(be_false)

      with it('enforces is_modifiable result'):
        self.constraints.enhance = False
        self.constraints.grayscale = False
        expect(calling(setattr, self.constraints, 'enhance', True)).to(
            raise_error(AttributeError, 'enhance is not modifiable'))
