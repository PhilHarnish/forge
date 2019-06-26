import numpy as np

from data.image import component_model
from spec.mamba import *

with description('component_model'):
  with it('instantiates without labels'):
    expect(calling(component_model.ComponentModel, np.zeros((3, 4)))).to(
        be_a(component_model.ComponentModel))

  with it('instantiates with labels'):
    expect(
        calling(
            component_model.ComponentModel,
            np.zeros((3, 4)),
            labels={'symbol': '6'},
        )).to(be_a(component_model.ComponentModel))
