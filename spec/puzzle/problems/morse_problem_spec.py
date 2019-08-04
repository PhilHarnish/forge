from puzzle.problems import morse_problem
from spec.mamba import *

SAMPLE = '- .... .. ... / .. ... / -- --- .-. ... . / -.-. --- -.. .'
PUZZLE = """
|.|..
.-|.-
|-.-.
|..-|
.-|-|
..|--
-|-.|
""".strip().split('\n')


with description('MorseProblem'):
  with description('score'):
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

    with it('matches morse "/" delimited'):
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

    with it('accepts PUZZLE'):
      expect(morse_problem.MorseProblem.score(PUZZLE)).to(be_above(.9))

    with it('rejects "puzzle"'):
      expect(morse_problem.MorseProblem.score(['puzzle'])).to(equal(0))

  with description('_generate_interpretations') as self:
    with before.all:
      self.fn = getattr(morse_problem, '_generate_interpretations')

    with it('suggests attempting a swap for clean input'):
      expect([tuple(pair) for _, pair in self.fn('...---...')]).to(
          equal([
            ('.', '-', None, None, set()),
            ('-', '.', None, None, set())
          ]))

    with it('resists attempting a swap for improbable but valid input'):
      expect([tuple(pair) for _, pair in self.fn('---...---')]).to(
          equal([
            ('.', '-', None, None, set()),
            ('-', '.', None, None, set())
          ]))

    with it('avoids interpreting . or - as character delimiter'):
      expect([tuple(pair) for _, pair in self.fn('--- ... ---')]).to(
          equal([
            ('.', '-', ' ', None, set()),
            ('-', '.', ' ', None, set())
          ]))

    with it('attempts to identify delimiters'):
      expect([tuple(pair) for _, pair in self.fn(SAMPLE)]).to(
          equal([
            ('.', '-', ' ', '/', set()),
            ('.', '-', ' ', None, {'/'}),
            ('.', '-', None, None, {'/', ' '}),
            ('-', '.', ' ', '/', set()),
            ('-', '.', ' ', None, {'/'}),
            ('-', '.', None, None, {'/', ' '}),
          ]))

    with it('cannot decide which delimiter is which'):
      expect([tuple(pair) for _, pair in self.fn('.../--- ...')]).to(
          equal([
            ('.', '-', '/', ' ', set()),
            ('.', '-', ' ', '/', set()),
            ('.', '-', '/', None, {' '}),
            ('.', '-', ' ', None, {'/'}),
            ('.', '-', None, None, {'/', ' '}),
            ('.', '-', None, None, {'/', ' '}),
            ('-', '.', '/', ' ', set()),
            ('-', '.', ' ', '/', set()),
            ('-', '.', '/', None, {' '}),
            ('-', '.', ' ', None, {'/'}),
            ('-', '.', None, None, {'/', ' '}),
            ('-', '.', None, None, {'/', ' '}),
          ]))

    with it('is willing to interpret puzzle with newlines'):
      expect([tuple(pair) for _, pair in self.fn('\n'.join(PUZZLE))]).to(
          equal([
            ('.', '-', '|', '\n', set()),
            ('.', '-', '|', None, {'\n'}),
            ('.', '-', None, None, {'|', '\n'}),
            ('-', '.', '|', '\n', set()),
            ('-', '.', '|', None, {'\n'}),
            ('-', '.', None, None, {'|', '\n'}),
          ]))

  with description('solutions'):
    with it('solves SOS'):
      solutions = morse_problem.MorseProblem('ex', ['... --- ...']).solutions()
      expect(solutions).to(have_keys('sos'))

    with it('solves SAMPLE'):
      solutions = morse_problem.MorseProblem('ex', [SAMPLE]).solutions()
      expect(solutions).to(have_keys('this is morse code', 'thisismorsecode'))
      expect(solutions['this is morse code']).to(
          be_above(solutions['thisismorsecode']))

    with it('solves PUZZLE'):
      solutions = morse_problem.MorseProblem('ex', PUZZLE).solutions()
      expect(solutions).to(have_key('evacuation'))

    with it('does not raise for "puzzle"'):
      problem = morse_problem.MorseProblem('ex', ['puzzle'])
      expect(calling(problem.solutions)).not_to(raise_error)
