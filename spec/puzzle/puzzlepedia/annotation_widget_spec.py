from puzzle.constraints import constraints, validator
from puzzle.puzzlepedia import annotation_widget
from spec.mamba import *


widget_patch = mock.patch('puzzle.puzzlepedia.annotation_widget.widgets')


class TestConstraints(constraints.Constraints):
  test: str = 'value'


with description('annotation_widget'):
  with before.each:
    self.mock_widgets = widget_patch.start()

  with after.each:
    widget_patch.stop()

  with it('renders NumberInRange as a FloatSlider'):
    annotation_widget.AnnotationWidget(
        validator.NumberInRange(0.0, 2.0), TestConstraints(), 'test', 1.0,
        mock.Mock())
    expect(self.mock_widgets.FloatSlider).to(have_been_called)
