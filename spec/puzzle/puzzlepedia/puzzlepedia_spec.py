from puzzle.puzzlepedia import puzzle, puzzlepedia
from spec.mamba import *

display_patch = mock.patch('puzzle.puzzlepedia.puzzlepedia.display')
prod_config_patch = mock.patch('puzzle.puzzlepedia.puzzlepedia.prod_config')

with description('puzzlepedia'):
  with before.each:
    self.puzzle = puzzle.Puzzle('test', '')
    self.mock_display = display_patch.start()
    self.mock_prod_config = prod_config_patch.start()

  with after.each:
    display_patch.stop()
    prod_config_patch.stop()
    puzzlepedia.reset()

  with it('does not initialize on import'):
    expect(puzzlepedia._INITIALIZED).to(be_false)

  with description('parse'):
    with it('initializes after calling parse'):
      puzzlepedia.parse('')
      expect(puzzlepedia._INITIALIZED).to(be_true)

  with description('interact_with'):
    with before.each:
      self.puzzle = puzzle.Puzzle('test', '')

    with it('runs without exception'):
      expect(calling(puzzlepedia.interact_with, self.puzzle)).not_to(
          raise_error)
