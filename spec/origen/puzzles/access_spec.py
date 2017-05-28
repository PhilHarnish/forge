from spec.mamba import *

if False:
  from data import data
  from origen import seven_segment
  from origen import seven_segment_data
  from origen.puzzles import access

  TEST_DATA = data.load(
      'data/seven_segment_prototype_test_data.txt',
      seven_segment.Glyphs)

with _description('combinations'):
  with it('should merge two characters'):
    merged = (
        seven_segment_data.ALPHABET['F'] |
        (seven_segment_data.ALPHABET['l'] >> 1))
    expect(merged).to(equal(seven_segment_data.ALPHABET['A']))

  with it('should accept ACCESS no-op'):
    expect(access.accept(seven_segment_data.ACCESS)).to(be_true)

  with it('should accept ACCESS after transformations'):
    transformed = (
        seven_segment_data.glyphs_from_str('ACCESS') |
        seven_segment_data.glyphs_from_str('ALL'))
    expect(access.accept(transformed)).to(be_true)

with _description('prototype test data'):
  with it('should load test data'):
    expect(TEST_DATA).to(have_keys('KEY', 'CORRECT', 'NOPE', 'LOST'))

  with it('KEY should merge with access and accept'):
    transformed = TEST_DATA['KEY'] | seven_segment_data.ACCESS
    expect(access.accept(transformed)).to(be_true)

  with it('CORRECT should merge with access and accept'):
    transformed = TEST_DATA['CORRECT'] | seven_segment_data.ACCESS
    expect(access.accept(transformed)).to(be_true)

  with it('KEY|CORRECT should merge with access and accept'):
    transformed = TEST_DATA['KEY'] | TEST_DATA['CORRECT']
    expect(access.accept(transformed)).to(be_true)

  with it('KEY|<others> should not accept'):
    for test in ['NOPE', 'LOST']:
      transformed = TEST_DATA['KEY'] | TEST_DATA[test]
      expect(access.accept(transformed)).not_to(be_true)

  with it('KEY|NOPE should contain nOPE'):
    transformed = TEST_DATA['KEY'] | TEST_DATA['NOPE']
    expected = seven_segment_data.glyphs_from_str('nOPE')
    expect(expected in transformed).to(be_true)

  with it('KEY|LOST should contain LOSt'):
    transformed = TEST_DATA['KEY'] | TEST_DATA['LOST']
    expected = seven_segment_data.glyphs_from_str('LOSt')
    expect(expected in transformed).to(be_true)

with _description('Numberjack models'):
  with it('creates a goal and key'):
    puzzle = access.AccessPuzzle(seven_segment_data.ACCESS, 0)
    expect(puzzle.goal).not_to(be_empty)
    expect(puzzle.key).not_to(be_empty)

  with it('creates a board'):
    puzzle = access.AccessPuzzle(seven_segment_data.ACCESS, 1)
    expect(puzzle.boards).not_to(be_empty)

  with it('solves 1 board'):
    puzzle = access.AccessPuzzle(seven_segment_data.ACCESS, 1)
    puzzle.solve()
    key = puzzle.get_key()
    board = puzzle.get_board(0)
    expect(key | board).to(equal(seven_segment_data.ACCESS))
