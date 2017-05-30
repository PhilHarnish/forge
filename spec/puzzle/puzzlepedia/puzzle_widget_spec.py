from puzzle.puzzlepedia import puzzle, puzzle_widget
from spec.mamba import *

widget_patch = mock.patch('puzzle.puzzlepedia.puzzle_widget.widgets')

with description('PuzzleWidget'):
  with before.each:
    self.puzzle = puzzle.Puzzle('test', '')
    self.mock_widgets = widget_patch.start()

  with after.each:
    widget_patch.stop()

  with it('instantiates with empty problems'):
    expect(calling(puzzle_widget.PuzzleWidget, self.puzzle)).not_to(
        raise_error)

  with it('creates an Accordion'):
    puzzle_widget.PuzzleWidget(self.puzzle)
    expect(self.mock_widgets.Accordion).to(have_been_called)
