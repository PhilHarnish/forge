import html
from typing import Any

from ipywidgets import widgets

from puzzle.steps import step


def DebugDataWidget(s: step.Step) -> widgets.Widget:
  data = s.get_debug_data()
  container = widgets.Accordion([_data_widget(data)])
  container.set_title(0, 'debug data')
  container.selected_index = -1
  return container


def _data_widget(data: Any) -> widgets.HTML:
  # TODO: Handle non-text data.
  return widgets.HTML(html.escape(str(data)).replace('\n', '<br />'))
