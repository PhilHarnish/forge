from puzzle.problems import morse_problem
from spec.mamba import *

SAMPLE = '- .... .. ... / .. ... / -- --- .-. ... . / -.-. --- -.. .'

with description('MorseProblem'):
  with it('ignores empty input'):
    expect(morse_problem.MorseProblem.score([''])).to(equal(0))

  with it('matches multiple lines'):
    expect(morse_problem.MorseProblem.score([
      '...',
      '---',
      '...',
    ])).to(equal(1))

  with it('matches morse explicitly'):
    expect(morse_problem.MorseProblem.score([
      '... --- ...'
    ])).to(equal(1))

  with it('matches morse "," delimited'):
    expect(morse_problem.MorseProblem.score([
      '.../---/...'
    ])).to(equal(1))

  with it('matches morse "|" delimited'):
    expect(morse_problem.MorseProblem.score([
      '...|---|...'
    ])).to(be_above(0.9))

  with it('scores longer non-morse strings than short ones'):
    long = morse_problem.MorseProblem.score(['aaabbbaaa'])
    short = morse_problem.MorseProblem.score(['aba'])
    expect(long).to(be_above(short))

  with it('scores dot and dash more confidently'):
    good = morse_problem.MorseProblem.score(['...;---;...'])
    ambiguous = morse_problem.MorseProblem.score(['aaa;bbb;aaa'])
    expect(good).to(be_above(ambiguous))

  with it('accepts SAMPLE'):
    expect(morse_problem.MorseProblem.score([SAMPLE])).to(equal(1))
