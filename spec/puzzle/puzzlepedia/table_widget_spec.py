from puzzle.puzzlepedia import table_widget
from spec.mamba import *

widget_patch = mock.patch('puzzle.puzzlepedia.table_widget.widgets')

with description('TableWidget'):
  with before.each:
    self.mock_widgets = widget_patch.start()

  with after.each:
    widget_patch.stop()

  with it('instantiates with empty ctor'):
    expect(calling(table_widget.TableWidget)).not_to(raise_error)

  with it('creates a VBox and HBox'):
    table_widget.TableWidget([], [])
    expect(self.mock_widgets.HTML).to(have_been_called)
