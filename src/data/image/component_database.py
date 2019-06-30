from typing import Dict

from data import warehouse
from data.image import component


class ComponentDatabase(object):
  _index: Dict[int, component.Component]

  def __init__(self) -> None:
    # Initial version uses a pre-identified index.
    self._index = warehouse.get('/image/components')

  def identify(self, c: component.Component) -> component.Component:
    identified = self._index.get(hash(c))
    if identified:
      c.labels.update(identified.labels)
    return c
