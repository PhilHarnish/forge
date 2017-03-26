from expects import *
from src.data import crossword


with description('clue_keywords'):
  with it('removes garbage characters'):
    expect(crossword.clue_keywords('-_-;;!')).to(be_empty)

  with it('removes common words'):
    expect(crossword.clue_keywords('for eg that abbr for the org')).to(be_empty)

  with it('removes (\d+)'):
    expect(crossword.clue_keywords('(11)')).to(be_empty)

  with it('ignores 1 character words'):
    expect(crossword.clue_keywords('a b c d e')).to(be_empty)

  with it('tokenizes and alphabetizes what remains'):
    expect(crossword.clue_keywords(
        'Vegetable that gives Popeye superhuman strength (7)'
    )).to(equal(['vegetable', 'gives', 'popeye', 'superhuman', 'strength']))
