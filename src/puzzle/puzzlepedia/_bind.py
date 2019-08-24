from typing import Any, Callable, ContextManager, Optional

import rx
from ipywidgets import widgets
from traitlets.utils import bunch

from data import types
from puzzle.constraints import constraints


def callback_without_event(
    fn: Callable[[Any], Any], *args: Any) -> Callable[[Any], None]:
  return lambda event: fn(*args)


def value_to_widget(
    group: constraints.Constraints,
    key: str,
    coerce: Optional[Callable[[Any], Any]],
    widget: widgets.DOMWidget,
    capture: ContextManager) -> None:
  source = widget_observable(widget)
  def _on_widget_change(value: Any) -> None:
    with capture:
      if not widget.disabled:
        if coerce is None:
          setattr(group, key, value)
        else:
          setattr(group, key, coerce(value))

  source.subscribe(_on_widget_change)


def clear_to_widget(
    group: constraints.Constraints,
    key: str,
    coerce: Optional[Callable[[Any], Any]],
    widget: widgets.DOMWidget,
    toggle_button: widgets.ToggleButton) -> None:
  source = widget_observable(toggle_button)
  def _on_button_change(enabled: bool) -> None:
    widget.disabled = not enabled
    if enabled:
      toggle_button.description = 'clear'
      if coerce is not None and widget.value is not None:
        setattr(group, key, coerce(widget.value))
    else:
      toggle_button.description = 'set'
      setattr(group, key, None)

  source.subscribe(_on_button_change)


def widget_observable(
    widget: widgets.DOMWidget, key: str = 'value') -> rx.AnonymousObservable:
  def subscribe(observer: types.Observer) -> None:
    def _on_change(change: bunch.Bunch) -> None:
      observer.on_next(change['new'])

    widget.observe(_on_change, names=key)

  return rx.AnonymousObservable(subscribe)
