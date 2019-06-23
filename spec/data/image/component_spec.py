import numpy as np

from data.image import component
from spec.mamba import *

with description('component'):
  with it('instantiates'):
    expect(calling(component.Component, np.zeros((3, 4)))).to(
        be_a(component.Component))

  with it('hashes same things consistently'):
    a = component.Component(np.zeros((3, 4)))
    b = component.Component(np.zeros((3, 4)))
    expect(hash(a)).to(equal(hash(b)))

  with it('hashes different things differently'):
    a = component.Component(np.zeros((3, 4)))
    b = component.Component(np.zeros((4, 3)))
    expect(hash(a)).not_to(equal(hash(b)))
