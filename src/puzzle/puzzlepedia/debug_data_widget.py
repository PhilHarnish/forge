import io
from typing import Any, ContextManager, Dict

import numpy as np
from PIL import Image
from ipywidgets import widgets

from puzzle.puzzlepedia import _bind, _common
from puzzle.steps import step


def DebugDataWidget(s: step.Step, capture: ContextManager) -> widgets.Widget:
  with capture:
    try:
      data = s.get_debug_data()
    except NotImplementedError:
      data = '[no data]'
    return _data_widget(data)


def _data_widget(data: Any) -> widgets.Widget:
  if (isinstance(data, list) and len(data) > 0 and
      isinstance(data[0], tuple) and len(data[0]) == 2 and
      isinstance(data[0][0], str)
  ):
    options = [label for label, _ in data]
    value = options[-1]
    data_widgets = {
      label: _data_widget(value) for label, value in data
    }
    slider = widgets.SelectionSlider(
        options=options,
        value=value,
        continuous_update=True,
    )
    children = [slider, data_widgets[value]]
    vbox = widgets.VBox(children)
    slider_changed = _bind.widget_observable(slider)
    slider_changed.subscribe(_bind.callback_without_event(
        _update_debug_data_vbox_children_from_slider, data_widgets, vbox))
    return vbox
  elif isinstance(data, np.ndarray) and data.dtype == np.uint8:
    return _ndarray_image(data)
  # Fallback assumes data is text.
  return widgets.HTML(_common.preformat_html(str(data)))


def _ndarray_image(data: np.ndarray) -> widgets.Widget:
  height, width = data.shape[:2]
  f = io.BytesIO()
  Image.fromarray(data).save(f, 'png')
  return widgets.Image(
      value=f.getvalue(),
      width=width,
      height=height,
  )


def _update_debug_data_vbox_children_from_slider(
    data_widgets: Dict[str, widgets.Widget],
    vbox: widgets.VBox) -> None:
  slider, _ = vbox.children
  vbox.children = [slider, data_widgets[slider.value]]
