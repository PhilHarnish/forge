from typing import Any, Iterable

from ipywidgets import widgets

from puzzle.constraints import constraints, validator
from puzzle.puzzlepedia import _bind, _common

_FLOAT_FORMAT = '0.2f'


def AnnotationWidget(
    annotation: constraints.Constraint,
    group: constraints.Constraints,
    key: str, value: Any) -> widgets.Widget:
  inner_optional = constraints.unwrap_optional(annotation)
  is_optional = bool(inner_optional)
  row = []
  if inner_optional:
    annotation = inner_optional
  if annotation in {int, float}:
    widget = widgets.FloatText(
        value=value,
        disabled=value is None,
        placeholder='None',
        readout_format=_FLOAT_FORMAT,
    )
    coerce = annotation
  elif isinstance(annotation, validator.NumberInRange):
    if annotation.max_value < float('inf'):
      widget = widgets.FloatSlider(
          value=value,
          min=annotation.min_value,
          max=annotation.max_value,
          disabled=value is None,
          continuous_update=False,
          placeholder='None',
          readout=True,
          readout_format=_FLOAT_FORMAT,
          step=0.01,
      )
      coerce = type(annotation.max_value)
    else:
      widget = widgets.BoundedFloatText(
          value=value,
          min=annotation.min_value,
          disabled=value is None,
          placeholder='None',
          readout_format=_FLOAT_FORMAT,
      )
      coerce = type(annotation.min_value)
  elif isinstance(annotation, type(Iterable)):
    if hasattr(annotation, '__args__') and len(annotation.__args__) == 1:
      coerce = annotation.__args__[0]
      child_type = coerce.__name__
    else:
      coerce = None
      child_type = '?'
    if value is None:
      label = None
    else:
      label = str(value)
    placeholder = ', '.join([child_type] * 3) + ', ...'
    widget = widgets.Text(
        value=label,
        placeholder=placeholder,
        disabled=value is None,
    )
  else:
    raise NotImplementedError(
        '%s: %s %s (%s)' % (key, value, annotation, type(annotation)))
  label_widget = widgets.Label(value=_common.format_label(key))
  label_widget.width = '25%'
  row.append(label_widget)
  row.append(widget)
  _bind.value_to_widget(group, key, coerce, widget)
  if is_optional:
    if value is None:
      description = 'set'
    else:
      description = 'clear'
    toggle_button = widgets.ToggleButton(
        value=value is not None,
        description=description,
        button_style='',
    )
    row.append(toggle_button)
    _bind.clear_to_widget(group, key, coerce, widget, toggle_button)
  return widgets.HBox(row)
