from typing import Any, List, Tuple

import cv2
import numpy as np

from data.image import coloring, image, lines_classifier, model, sliced_grid
from puzzle.constraints import constraints
from puzzle.constraints.image import identify_regions_constraints, \
  lines_classifier_constraints, sliced_grid_constraints
from puzzle.steps.image import _base_image_step, prepare_image


class IdentifyRegions(_base_image_step.BaseImageStep):
  _prepare_image_step: prepare_image.PrepareImage
  _identify_regions_constraints: (
      identify_regions_constraints.IdentifyRegionsConstraints)
  _lines_classifier: lines_classifier.LinesClassifier
  _lines_classifier_constraints: (
    lines_classifier_constraints.LinesClassifierConstraints)
  _sliced_grid: sliced_grid.SlicedGrid
  _sliced_grid_constraints: (
      sliced_grid_constraints.SlicedGridConstraints)

  def __init__(
      self,
      prepare_image_step: prepare_image,
      step_constraints: identify_regions_constraints.IdentifyRegionsConstraints,
  ) -> None:
    self._prepare_image_step = prepare_image_step
    self._prepare_image_step.subscribe(self._on_source_changed)
    source = self._prepare_image_step.get_result()
    self._lines_classifier_constraints = (
        lines_classifier_constraints.LinesClassifierConstraints())
    step_constraints.register_method_constraint(
        self._lines_classifier_constraints)
    self._sliced_grid_constraints = (
        sliced_grid_constraints.SlicedGridConstraints(source))
    step_constraints.register_method_constraint(
        self._sliced_grid_constraints)
    super().__init__(
        source,
        dependencies=[self._prepare_image_step],
        constraints=[
          step_constraints,
          self._lines_classifier_constraints,
          self._sliced_grid_constraints,
        ])
    self._identify_regions_constraints = step_constraints
    self._lines_classifier = lines_classifier.LinesClassifier(
        source, self._lines_classifier_constraints)
    self._sliced_grid = sliced_grid.SlicedGrid(
        source, self._sliced_grid_constraints)

  def get_debug_data(self) -> List[Tuple[str, Any]]:
    result = super().get_debug_data()
    method = self._identify_regions_constraints.method
    if method == identify_regions_constraints.Method.LINES_CLASSIFIER:
      result.append(('lines', self._lines_classifier.get_debug_data()))
      for spec in self._lines_classifier.line_specs():
        break
      else:
        spec = None
    elif method == identify_regions_constraints.Method.SLICED_GRID:
      result.append(('sliced', self._sliced_grid.get_debug_data()))
      spec = self._sliced_grid
    else:
      raise NotImplementedError('Unsupported method %s' % method)
    if spec:
      result.append(('classified', self._draw_debug_data(spec)))
    else:
      result.append(('classified', 'classification failed'))
    return result

  def _modify_result(self, result: image.Image) -> image.Image:
    return result

  def _on_constraints_changed(
      self, change: constraints.ConstraintChangeEvent) -> None:
    if not change.key:
      return  # Ignore cosmetic changes.
    self._lines_classifier = lines_classifier.LinesClassifier(
        self._source, self._lines_classifier_constraints)
    super()._on_constraints_changed(change)

  def _on_source_changed(
      self, change: _base_image_step.ImageChangeEvent) -> None:
    del change
    source = self._prepare_image_step.get_result()
    self._source = source
    self._sliced_grid.set_source(source)

  def _draw_debug_data(self, spec: model.LineSpecification) -> np.ndarray:
    data = cv2.cvtColor(self._source.get_debug_data(), cv2.COLOR_GRAY2RGB)
    mask = np.zeros_like(data)
    colors = coloring.colors(len(spec))
    for divisions, color in zip(spec, colors):
      for theta, a, b, pos in divisions:
        if pos == 0 or pos == 1:
          cv2.line(data, a, b, color, thickness=3)
        else:
          cv2.line(data, a, b, color, thickness=1)
        cv2.line(
            mask, a, b, color,
            thickness=self._identify_regions_constraints.line_thickness)
    return np.where(mask > 0, data, data // 2)
