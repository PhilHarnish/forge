from data import warehouse
from puzzle.problems import number_problem
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

with description('number_problem end2end', 'end2end'):
  with before.all:
    warehouse.save()
    prod_config.init()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('solves simple problems'):
    problem = number_problem.NumberProblem(
        'ex',
        ['0xCAB'])  # 6546
    solutions = problem.solutions()
    solution, weight = solutions.first()
    expect(solution).to(equal('cab'))
    expect(weight).to(be_above(0))

  with it('solves real problems with increment'):
    problem = number_problem.NumberProblem(
        'BINARY +1',
        ['300451275870959962186'])
    solutions = problem.solutions()
    solution, weight = solutions.first()
    expect(solution).to(equal('binary +1'))
    expect(weight).to(be_above(0))

  with it('solves more problems with even more increment'):
    problem = number_problem.NumberProblem(
        'DECIMAL +25',
        ['29165720900'])
    solutions = problem.solutions()
    expect(solutions).to(have_key('decimal +25'))
    # TODO: The score for this should be *way* higher.
    expect(solutions['decimal +25']).to(be_between(.18, .2))

  with it('solves binary (without increment)'):
    problem = number_problem.NumberProblem(
        'NO AIR +0',
        ['01110 01111 00001 01001 10010'])
    solutions = problem.solutions()
    expect(solutions).to(have_key('no air'))
    expect(solutions['no air']).to(be_above(.95))

  with it('solves GPH 2018 overtime'):
    problem = number_problem.NumberProblem(
        'TETRADECIMAL + 14',
        ['459601727585320977851323670'])
    solutions = problem.solutions()
    expect(solutions).to(have_key('tetra decimal +14'))
    expect(solutions['tetra decimal +14']).to(be_above(.50))

  with it('solves mspc'):
    input = """
      0x500072 0x69007A 0x650061 0x770061 0x720064 0x650064 0x74006F 0x610075
      0x740068 0x6F0072 0x66006F 0x720074 0x680069 0x730062 0x6F006F 0x6B002E
    """.split('\n')
    problem = number_problem.NumberProblem(
        'mspc',
        input,
        allow_offsets=False,
    )
    solutions = problem.solutions()
    solution, weight = solutions.first()
    expect(solution).to(equal('Prizeawardedtoauthorforthisbook.'))
    expect(weight).to(be_above(0))

  with it('solves MSPC devils on third'):
    input = [
      '14 7 49 14 70 23 71',
      '22 1 70 23 26 43 70 5 16 22 13',
      '5 49 52 40 5 67 1 2 49 1 2 2 1 16 13',
      '22 5 71 13 4 7 17 1 1 23',
      '43 4 41 1 13 77 14 5 16 1 22',
      '49 26 7 1 49 4 1 13 2 7 14 8 67 1 16',
      '13 52 26 7 25 1',
    ]
    problems = [number_problem.NumberProblem(
        'mspc',
        [line],
        allow_offsets=False,
    ) for line in input]
    expected_solutions = [
      'unlucky',
      'deck of cards',
      'alphabet letters',
      'days in week',
      'five squared',
      'loneliest number',
      'sponge',
    ]
    for problem, expected in zip(problems, expected_solutions):
      solutions = problem.solutions()
      expect(solutions).to(have_key(expected))
      expect(solutions[expected]).to(be_above(0))

  with it('solves "mystery experiences" Rachel'):
    problem = number_problem.NumberProblem(
        'Rachel',
        ['1212 21 12 1211 111 221 2222 2 21 212 11 2'])
    solutions = problem.solutions()
    solution, weight = solutions.first()
    expect(solution).to(equal('can you hear me'))
    expect(weight).to(be_above(0))
