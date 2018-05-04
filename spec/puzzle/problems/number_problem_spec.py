from puzzle.problems import number_problem
from spec.mamba import *

with description('NumberProblem'):
  with it('ignores empty input'):
    expect(number_problem.NumberProblem.score([''])).to(equal(0))

  with it('rejects pseudo-numbers'):
    expect(number_problem.NumberProblem.score(['1.2.3'])).to(equal(0))

  with it('accepts integers'):
    expect(number_problem.NumberProblem.score(['123'])).to(be_above(0))

  with it('accepts hex'):
    expect(number_problem.NumberProblem.score(['0xDEADBEEF'])).to(be_above(0))

  with it('accepts octal'):
    expect(number_problem.NumberProblem.score(['0777'])).to(be_above(0))

  with it('reluctantly accepts 0'):
    expect(number_problem.NumberProblem.score(['0'])).to(be_between(0, .000001))

  with it('accepts sequences in arbitrary base'):
    expect(number_problem.NumberProblem.score(['8 4 10 13 7 2 3 1 1'])).to(
        equal(1))

  with it('accepts sequences in arbitrary base, part deux'):
    expect(number_problem.NumberProblem.score([
      '01110 01111 00001 01001 10010'])).to(equal(1))

  with it('favors data with more information density'):
    expect(number_problem.NumberProblem.score(['1234'])).to(be_above(
        number_problem.NumberProblem.score(['123'])
    ))

  with description('_parse'):
    with it('parses enormous, well-formed inputs'):
      parsed = number_problem._parse([
        '0x500072 0x69007A 0x770061 0x720064 0x650064 0x74006F 0x610075',
        '0x740068',  # 0x6F0072 0x720074 0x680069 0x730062 0x6F006F 0x6B002E
      ])
      expect(parsed).to(equal([
        0x500072, 0x69007A, 0x770061, 0x720064, 0x650064, 0x74006F, 0x610075,
        0x740068,
      ]))
