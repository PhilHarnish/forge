from typing import Dict, Optional

from data import warehouse
from data.image import component, component_model


class ComponentDatabase(object):
  _index: Dict[int, component_model.ComponentModel]

  def __init__(self) -> None:
    # Initial version uses a pre-identified index.
    self._index = warehouse.get('/image/components')

  def identify(
      self, c: component.Component) -> Optional[component_model.ComponentModel]:
    return self._index.get(hash(c))
