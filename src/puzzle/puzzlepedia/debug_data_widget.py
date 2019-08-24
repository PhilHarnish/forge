import io
from typing import Any

import numpy as np
from PIL import Image
from ipywidgets import widgets

from puzzle.puzzlepedia import _common
from puzzle.steps import step


def DebugDataWidget(s: step.Step) -> widgets.Widget:
  # TODO: Make data fetching lazy?
  try:
    data = s.get_debug_data()
  except NotImplementedError:
    data = '[no data]'
  return _data_widget(data)


def _data_widget(data: Any) -> widgets.Widget:
  if isinstance(data, np.ndarray) and data.dtype == np.uint8:
    width, height = data.shape[:2]
    f = io.BytesIO()
    Image.fromarray(data).save(f, 'png')
    return widgets.Image(
        value=f.getvalue(),
        width=width,
        height=height,
    )
  # Fallback assumes data is text.
  return widgets.HTML(_common.preformat_html(str(data)))
