from tkinter import Tk
from typing import List, Optional, Union

import numpy as np
from IPython import display
from PIL import ImageGrab

from puzzle.heuristics import analyze
from puzzle.puzzlepedia import prod_config, puzzle, puzzle_widget

_INITIALIZED = False


def parse(
    source: Optional[puzzle.PuzzleSources] = None,
    hint: analyze.Hint = None,
    threshold: float = None):
  _init()
  if source is None:
    source = _get_clipboard()
  if threshold is None:
    result = puzzle.Puzzle('first stage', source, hint=hint)
  else:
    result = puzzle.Puzzle(
        'first stage', source, hint=hint, threshold=threshold)
  interact_with(result)
  return result


def interact_with(puzzle: puzzle.Puzzle) -> None:
  _init()
  display.display(puzzle_widget.PuzzleWidget(puzzle))


def initialized() -> bool:
  return _INITIALIZED


def _init() -> None:
  global _INITIALIZED
  if not _INITIALIZED:
    _INITIALIZED = True
    prod_config.reset()
    prod_config.init()


def reset() -> None:
  global _INITIALIZED
  _INITIALIZED = False
  prod_config.reset()


def _get_clipboard() -> Union[np.ndarray, List[str]]:
  image_grab = ImageGrab.grabclipboard()
  if image_grab:
    return np.array(image_grab)
  return [Tk().clipboard_get()]
