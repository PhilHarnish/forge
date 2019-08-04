from data import warehouse
from puzzle.puzzlepedia import prod_config, puzzle, puzzlepedia
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
    expect(puzzlepedia.initialized()).to(be_false)

  with description('parse'):
    with it('initializes after calling parse'):
      puzzlepedia.parse('')
      expect(puzzlepedia.initialized()).to(be_true)

    with it('does not read from clipboard if input is given'):
      with mock.patch(
          'puzzle.puzzlepedia.puzzlepedia._get_clipboard', return_value=''
      ) as patched_clipboard:
        puzzlepedia.parse('')
        expect(patched_clipboard).not_to(have_been_called)

    with it('reads from clipboard if no input is given'):
      with mock.patch(
          'puzzle.puzzlepedia.puzzlepedia._get_clipboard', return_value=''
      ) as patched_clipboard:
        puzzlepedia.parse()
        expect(patched_clipboard).to(have_been_called)

  with description('interact_with'):
    with before.each:
      self.puzzle = puzzle.Puzzle('test', '')

    with it('runs without exception'):
      expect(calling(puzzlepedia.interact_with, self.puzzle)).not_to(
          raise_error)

with _description('regression tests'):
  with before.all:
    warehouse.save()
    prod_config.init()

  with it('parses clues in order'):
    source = textwrap.dedent("""
      Classic Billy Wilder movie (4 wds)
      It ended with the Siege of Yorktown (2 wds)
      It may warn you of suprising object sizes (3 wds)
      Like most solid objects, as opposed to linear (hyph.)
      One who studies the spread of diseases
      The point in the orbit of a planet at which its closest to the sun
      Something asked intended to provoke a specific response (2 wds)
      Sort of valuable, like some gemstones
      Thoughtful discussion, as before a bill
    """).strip()
    lines = source.split('\n')
    p = puzzle.Puzzle('ex', source)
    expect(p.problems()).to(have_len(len(lines)))
    for problem, line in zip(p.problems(), lines):
      expect(problem.lines).to(equal([line]))
