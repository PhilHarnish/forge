from puzzle.problems.logic_test import tmp_hax
from spec.mamba import *

_QUESTION = """
Which of the following statements is correct?
Exactly one of answers A and C is correct.
Neither answer A nor answer C is correct.
Either answer D or E is correct (possibly both).
Answer A is incorrect.
Exactly one of answers C and D is correct.
"""
_QUIZ = """
Which of the following statements is correct?
Exactly one of answers A and C is correct.
Neither answer A nor answer C is correct.
Either answer D or E is correct (possibly both).
Answer A is incorrect.
Exactly one of answers C and D is correct.
Which of the following statements is correct?
Either answer A or E is correct (possibly both).
Neither answer B nor answer E is correct.
Answers D and E are not both correct.
Answers B and C are correct.
Answers B and D are not both correct.
Which of the following statements is correct?
Either answer D or E is correct (possibly both).
Answer E is correct.
Neither answer A nor answer D is correct.
Either answer A or D is correct (possibly both).
Neither answer B nor answer D is correct.
Which of the following statements is correct?
Answer E is incorrect.
Exactly one of answers C and D is correct.
Either answer C or E is correct (possibly both).
Answers B and C are correct.
Answers C and E are correct.
Which of the following statements is correct?
Answers C and D are not both correct.
Answers A and E are not both correct.
Either answer A or D is correct (possibly both).
Either answer A or C is correct (possibly both).
Answer C is correct.
Which of the following statements is correct?
Exactly one of answers B and D is correct.
Neither answer A nor answer E is correct.
Answer D is incorrect.
Answers B and E are not both correct.
Exactly one of answers C and D is correct.
Which of the following statements is correct?
Exactly one of answers A and D is correct.
Either answer A or D is correct (possibly both).
Answer E is correct.
Answers B and E are correct.
Answers A and D are not both correct.
Which of the following statements is correct?
Answer D is correct.
Either answer C or E is correct (possibly both).
Answers A and B are not both correct.
Exactly one of answers D and E is correct.
Neither answer A nor answer B is correct.
Which of the following statements is correct?
Answers A and B are correct.
Neither answer B nor answer C is correct.
Either answer B or C is correct (possibly both).
Answer A is correct.
Answer C is correct.
Which of the following statements is correct?
Answers A and D are correct.
Answers D and E are not both correct.
Either answer B or C is correct (possibly both).
Answers C and D are not both correct.
Either answer A or C is correct (possibly both).
Which of the following statements is correct?
Answers B and C are not both correct.
Answer B is correct.
Answers A and B are correct.
Answer A is correct.
Either answer A or D is correct (possibly both).
"""
_EXPECTED = """
A == (A != C)  # Exactly one of answers A and C is correct.
B == ((not A) & (not C))  # Neither answer A nor answer C is correct.
C == (D | E)  # Either answer D or E is correct (possibly both).
D == (not A)  # Answer A is incorrect.
E == (C != D)  # Exactly one of answers C and D is correct.

A == (A | E)  # Either answer A or E is correct (possibly both).
B == ((not B) & (not E))  # Neither answer B nor answer E is correct.
C == (not (D & E))  # Answers D and E are not both correct.
D == (B & C)  # Answers B and C are correct.
E == (not (B & D))  # Answers B and D are not both correct.

A == (D | E)  # Either answer D or E is correct (possibly both).
B == E  # Answer E is correct.
C == ((not A) & (not D))  # Neither answer A nor answer D is correct.
D == (A | D)  # Either answer A or D is correct (possibly both).
E == ((not B) & (not D))  # Neither answer B nor answer D is correct.

A == (not E)  # Answer E is incorrect.
B == (C != D)  # Exactly one of answers C and D is correct.
C == (C | E)  # Either answer C or E is correct (possibly both).
D == (B & C)  # Answers B and C are correct.
E == (C & E)  # Answers C and E are correct.

A == (not (C & D))  # Answers C and D are not both correct.
B == (not (A & E))  # Answers A and E are not both correct.
C == (A | D)  # Either answer A or D is correct (possibly both).
D == (A | C)  # Either answer A or C is correct (possibly both).
E == C  # Answer C is correct.

A == (B != D)  # Exactly one of answers B and D is correct.
B == ((not A) & (not E))  # Neither answer A nor answer E is correct.
C == (not D)  # Answer D is incorrect.
D == (not (B & E))  # Answers B and E are not both correct.
E == (C != D)  # Exactly one of answers C and D is correct.

A == (A != D)  # Exactly one of answers A and D is correct.
B == (A | D)  # Either answer A or D is correct (possibly both).
C == E  # Answer E is correct.
D == (B & E)  # Answers B and E are correct.
E == (not (A & D))  # Answers A and D are not both correct.

A == D  # Answer D is correct.
B == (C | E)  # Either answer C or E is correct (possibly both).
C == (not (A & B))  # Answers A and B are not both correct.
D == (D != E)  # Exactly one of answers D and E is correct.
E == ((not A) & (not B))  # Neither answer A nor answer B is correct.

A == (A & B)  # Answers A and B are correct.
B == ((not B) & (not C))  # Neither answer B nor answer C is correct.
C == (B | C)  # Either answer B or C is correct (possibly both).
D == A  # Answer A is correct.
E == C  # Answer C is correct.

A == (A & D)  # Answers A and D are correct.
B == (not (D & E))  # Answers D and E are not both correct.
C == (B | C)  # Either answer B or C is correct (possibly both).
D == (not (C & D))  # Answers C and D are not both correct.
E == (A | C)  # Either answer A or C is correct (possibly both).

A == (not (B & C))  # Answers B and C are not both correct.
B == B  # Answer B is correct.
C == (A & B)  # Answers A and B are correct.
D == A  # Answer A is correct.
E == (A | D)  # Either answer A or D is correct (possibly both).
""".strip()

with _description('tmp_hax') as self:
  with description('parse'):
    with description('options'):
      with it('reads simple assertion'):
        expect(str(tmp_hax.parse_option(
            'Answer A is incorrect.'))
        ).to(equal('A == (not A)  # Answer A is incorrect.'))

      with it('reads exactly 1 of 2'):
        expect(str(tmp_hax.parse_option(
            'Exactly one of answers A and C is correct.'))
        ).to(equal(
            'A == (A != C)  # Exactly one of answers A and C is correct.'))

      with it('reads neither nor'):
        expect(str(tmp_hax.parse_option(
            'Neither answer A nor answer C is correct.'))
        ).to(equal(
            'A == ((not A) & (not C))'
            '  # Neither answer A nor answer C is correct.'))

      with it('reads or'):
        expect(str(tmp_hax.parse_option(
            'Either answer D or E is correct (possibly both).'))
        ).to(equal(
            'A == (D | E)'
            '  # Either answer D or E is correct (possibly both).'))

    with description('questions'):
      with it('reads questions'):
        expect(tmp_hax.parse_questions(_QUIZ)).to(have_len(11))

      with it('produces asserts'):
        questions = []
        for question in tmp_hax.parse_questions(_QUIZ):
          questions.append(str(question))
        expect('\n\n'.join(questions)).to(equal(_EXPECTED))

  with description('solve'):
    with it('solves sample question'):
      expect(tmp_hax.solve(_QUESTION)).to(equal(''))
