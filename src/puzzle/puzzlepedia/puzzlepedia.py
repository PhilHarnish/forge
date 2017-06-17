from IPython import display

from puzzle.puzzlepedia import prod_config, puzzle, puzzle_widget

_INITIALIZED = False


def parse(source, hint=None):
  _init()
  result = puzzle.Puzzle('first stage', source, hint=hint)
  interact_with(result)
  return result


def interact_with(puzzle):
  _init()
  display.display(puzzle_widget.PuzzleWidget(puzzle))


def _init():
  global _INITIALIZED
  if not _INITIALIZED:
    _INITIALIZED = True
    prod_config.init()


def reset():
  global _INITIALIZED
  _INITIALIZED = False
  prod_config.reset()
