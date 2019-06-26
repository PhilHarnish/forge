from typing import Dict

from data.image import component as base_component

Labels = Dict[str, str]


class ComponentModel(object):
  component: base_component.Component
  labels: Labels

  def __init__(
      self, component: base_component.Component, labels: Labels = None) -> None:
    self.component = component
    self.labels = {}
    if labels:
      self.labels.update(labels)
