from ipywidgets import widgets

from puzzle.puzzlepedia import _widget_util
from spec.mamba import *

with description('merge_assign_widget'):
  with it('requires a list to merge'):
    dst = widgets.VBox(children=[widgets.Text(value='test')])
    expect(calling(_widget_util.merge_assign_children, dst, {})).to(
        raise_error(NotImplementedError))

  with it('refuses to merge if dst already has children'):
    dst = widgets.VBox(children=[widgets.Text(value='test')])
    expect(calling(_widget_util.merge_assign_children, dst, [
      widgets.Text(value='a'),
      widgets.Text(value='b'),
    ])).to(raise_error(NotImplementedError))

  with it('operates recursively'):
    dst_children = [
      widgets.Text(value='1'),
      widgets.Text(value='2'),
    ]
    dst = widgets.VBox(children=dst_children)
    children = [
      widgets.Text(value='a'),
      widgets.Text(value='b'),
    ]
    patch = 'puzzle.puzzlepedia._widget_util.merge_assign_widget'
    with mock.patch(patch) as merge_assign_widget:
      _widget_util.merge_assign_children(dst, children)
      expect(merge_assign_widget).to(have_been_called_times(2))
      expect(merge_assign_widget.call_args_list).to(equal([
        mock.call(children[0], dst_children[0]),
        mock.call(children[1], dst_children[1]),
      ]))


with description('merge_assign_widget'):
  with it('copies properties from one widget to another'):
    src = widgets.Text(value='source')
    dst = widgets.Text(value='destination')
    _widget_util.merge_assign_widget(src, dst)
    expect(dst).to(have_property('value', 'source'))

  with it('does not copy properties when types do not match'):
    src = widgets.Text(value='source')
    dst = widgets.HTML(value='destination')
    _widget_util.merge_assign_widget(src, dst)
    expect(dst).to(have_property('value', 'destination'))
