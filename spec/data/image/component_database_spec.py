from data.image import component_database
from spec.mamba import *


with description('component_database'):
  with it('instantiates'):
    expect(calling(component_database.ComponentDatabase)).to(
        be_a(component_database.ComponentDatabase))
