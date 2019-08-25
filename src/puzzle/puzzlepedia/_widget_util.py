from typing import Any

from ipywidgets import widgets


def merge_assign_children(dst: widgets.Widget, value: Any) -> None:
  original = getattr(dst, 'children')
  if not isinstance(value, (tuple, list)):
    raise NotImplementedError('Unable to merge type %s' % type(value))
  if len(original) != len(value):
    if not original:  # First time.
      setattr(dst, 'children', value)
      return
    raise NotImplementedError('Unable to merge lists of different lengths')
  for child_src, child_dst in zip(value, original):
    if (isinstance(child_src, widgets.Widget) and
        isinstance(child_dst, widgets.Widget)):
      merge_assign_widget(child_src, child_dst)

def merge_assign_widget(src: widgets.Widget, dst: widgets.Widget) -> None:
  if type(src) != type(dst):
    return
  for key in src.keys:
    if key.startswith('_'):
     continue
    value = getattr(src, key)
    if key == 'children':
      merge_assign_children(dst, value)
    elif getattr(dst, key) != value:
      setattr(dst, key, value)
