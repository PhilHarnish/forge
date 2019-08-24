import enum
from typing import Any, ContextManager, Iterable

from ipywidgets import widgets

from puzzle.constraints import constraints, validator
from puzzle.puzzlepedia import _bind, _common

_FLOAT_FORMAT = '0.2f'


def AnnotationWidget(
    annotation: constraints.Constraint,
    group: constraints.Constraints,
    key: str, value: Any,
    capture: ContextManager) -> widgets.Widget:
  inner_optional = constraints.unwrap_optional(annotation)
  is_optional = bool(inner_optional)
  row = []
  if inner_optional:
    annotation = inner_optional
  if annotation in {int, float}:
    widget = widgets.FloatText(
        value=value,
        placeholder='None',
        readout_format=_FLOAT_FORMAT,
    )
    coerce = annotation
  elif annotation == bool:
    widget = widgets.Checkbox(
        value=value,
    )
    coerce = annotation
  elif isinstance(annotation, type) and issubclass(annotation, enum.Enum):
    options = [
      (_common.format_label(option.name), option) for option in annotation
    ]
    widget = widgets.Dropdown(
        options=options,
        value=value,
    )
    coerce = annotation
  elif isinstance(annotation, validator.Color):
    widget = widgets.ColorPicker(value=annotation.to_rgb_hex(value))
    coerce = annotation.coerce
  elif isinstance(annotation, validator.NumberInRange):
    if annotation.max_value < float('inf'):
      coerce = type(annotation.max_value)
    else:
      coerce = type(annotation.min_value)
    if coerce is float:
      slider_widget = widgets.FloatSlider
      text_widget = widgets.BoundedFloatText
      readout_format = _FLOAT_FORMAT
      step = 0.01
    else:
      slider_widget = widgets.IntSlider
      text_widget = widgets.BoundedIntText
      readout_format = 'd'
      step = 1
    if annotation.max_value < float('inf'):
      widget = slider_widget(
          value=value,
          min=annotation.min_value,
          max=annotation.max_value,
          continuous_update=False,
          readout_format=readout_format,
          step=step,
      )
    else:
      widget = text_widget(
          value=value,
          min=annotation.min_value,
          readout_format=readout_format,
      )
  elif isinstance(annotation, validator.Point):
    widget = widgets.Text(
        value=repr(value),
    )
    coerce = annotation.from_str
  elif isinstance(annotation, validator.RangeInRange):
    if type(annotation.min_value) is int:
      range_slider = widgets.IntRangeSlider
    else:
      range_slider = widgets.FloatRangeSlider
    widget = range_slider(
        value=value,
        min=annotation.min_value,
        max=annotation.max_value,
        continuous_update=False,
    )
    coerce = list
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
    )
  else:
    raise NotImplementedError(
        '%s: %s %s (%s)' % (key, value, annotation, type(annotation)))
  label_widget = widgets.Label(value=_common.format_label(key))
  label_widget.layout.width = '25%'
  row.append(label_widget)
  row.append(widget)
  _bind.value_to_widget(group, key, coerce, widget, capture)
  if is_optional:
    if value is None:
      description = 'set'
    else:
      description = 'clear'
    toggle_button = widgets.ToggleButton(
        value=value is not None,
        description=description,
    )
    row.append(toggle_button)
    _bind.clear_to_widget(group, key, coerce, widget, toggle_button)
    _set_disabled(toggle_button, group, key, False)
    group.subscribe(
        _bind.callback_without_event(
            _set_disabled, toggle_button, group, key, False))
  _set_disabled(widget, group, key, True)
  group.subscribe(
      _bind.callback_without_event(_set_disabled, widget, group, key, True))
  return widgets.HBox(row)


def _set_disabled(
    widget: widgets.Widget,
    group: constraints.Constraints,
    key: str,
    consider_value: bool) -> None:
  disabled_value = consider_value and getattr(group, key) is None
  widget.disabled = not group.is_modifiable(key) or disabled_value
