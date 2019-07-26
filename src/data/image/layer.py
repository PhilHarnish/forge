from typing import List

from data.image import component


class Layer(object):
  def __init__(self, kind: str, components: List[component.Component]) -> None:
    self.kind = kind
    self.components = components
