from data import crossword, warehouse
from spec.mamba import *

with description('clue_keywords'):
  with it('removes garbage characters'):
    expect(crossword.clue_keywords('-_-;;!')).to(be_empty)

  with it('removes common words'):
    expect(crossword.clue_keywords('for eg that abbr for the org')).to(be_empty)

  with it('removes (11)'):
    expect(crossword.clue_keywords('(11)')).to(be_empty)

  with it('removes (3, 4)'):
    expect(crossword.clue_keywords('(3, 4)')).to(be_empty)
    expect(crossword.clue_keywords('(3,4)')).to(be_empty)

  with it('removes (3|4)'):
    expect(crossword.clue_keywords('(3|4)')).to(be_empty)

  with it('ignores 1 character words'):
    expect(crossword.clue_keywords('a b c d e')).to(be_empty)

  with it('tokenizes and alphabetizes what remains'):
    expect(crossword.clue_keywords(
        'Vegetable that gives Popeye superhuman strength (7)'
    )).to(equal(['vegetable', 'gives', 'popeye', 'superhuman', 'strength']))


with description('db'):
  with before.all:
    conn, self.cursor = warehouse.get('/phrases/crossword')
    crossword.add(self.cursor, 'blue', 1, {'color': 1, 'emotion': 1})
    crossword.add(self.cursor, 'orange', 2, {'color': 1, 'fruit': 1})
    crossword.add(self.cursor, 'green', 2, {'color': 1, 'envy': 1, 'money': 1})
    conn.commit()

  with it('returns empty results for garbage'):
    expect(crossword.query(self.cursor, 'dfsafsfasdfasdfas')).to(be_empty)

  with it('returns specific results'):
    results = crossword.query(self.cursor, 'color or emotion')
    expect(results).not_to(be_empty)
    expect(results[0]).to(contain('blue'))

  with it('accepts partial matches'):
    results = crossword.query(self.cursor, 'color of money')
    expect(results).not_to(be_empty)
    expect(results[0]).to(contain('green'))
