from data import meta
from puzzle.puzzlepedia import problem_widget
from spec.mamba import *

widget_patch = mock.patch('puzzle.puzzlepedia.problem_widget.widgets')
table_patch = mock.patch('puzzle.puzzlepedia.problem_widget.table_widget')


with description('ProblemWidget'):
  with before.each:
    self.meta_problems = meta.Meta()
    self.mock_widgets = widget_patch.start()
    self.mock_table = table_patch.start()

  with after.each:
    widget_patch.stop()
    table_patch.stop()

  with it('instantiates with empty problems'):
    expect(calling(problem_widget.ProblemWidget, self.meta_problems)).not_to(
        raise_error)

  with it('creates a VBox and HBox'):
    problem_widget.ProblemWidget(self.meta_problems)
    expect(self.mock_widgets.HBox).to(have_been_called)
    expect(self.mock_widgets.VBox).to(have_been_called)
