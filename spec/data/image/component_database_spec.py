import numpy as np

from data import warehouse
from data.image import component, component_database
from spec.mamba import *

_INDEX = {}


def _get_components() -> Dict[int, component.Component]:
  return _INDEX


def _add_to_index(image: np.ndarray, labels: dict) -> None:
  c = component.Component(image, labels=labels)
  _INDEX[hash(c)] = c


with description('component_database'):
  with before.all:
    warehouse.save()
    warehouse.register('/image/components', _get_components)

  with after.all:
    warehouse.restore()

  with it('instantiates'):
    expect(calling(component_database.ComponentDatabase)).to(
        be_a(component_database.ComponentDatabase))

  with description('identify') as self:
    with before.all:
      self.full_box = np.ones((3, 3))
      _add_to_index(self.full_box, labels={'symbol': 'FULL'})
      self.empty_box = np.zeros((3, 3))
      _add_to_index(self.empty_box, {'symbol': 'EMPTY'})
      self.db = component_database.ComponentDatabase()

    with it('ignores unknown components'):
      c = component.Component(np.ones((2, 2)))
      expect(self.db.identify(c).labels).to(be_empty)

    with it('adds labels to known components'):
      c = component.Component(np.ones((3, 3)))
      expect(self.db.identify(c).labels).to(equal({'symbol': 'FULL'}))
