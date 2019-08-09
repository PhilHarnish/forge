from puzzle.puzzlepedia import debug_data_widget
from puzzle.steps import step
from spec.mamba import *


class TestStep(step.Step):
  def get_debug_data(self) -> Any:
    return 'sample'


widget_patch = mock.patch('puzzle.puzzlepedia.debug_data_widget.widgets')


with description('debug_data_widget'):
  with before.each:
    self.mock_widgets = widget_patch.start()

  with after.each:
    widget_patch.stop()

  with it('catches exception when no data is available'):
    expect(calling(debug_data_widget.DebugDataWidget, step.Step())).not_to(
        raise_error(NotImplementedError))

  with it('returns a widget when possible'):
    debug_data_widget.DebugDataWidget(TestStep())
    expect(self.mock_widgets.HTML).to(have_been_called)
