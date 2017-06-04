from data import warehouse
from puzzle.problems import cryptogram_problem
from puzzle.puzzlepedia import prod_config
from spec.data import fixtures
from spec.mamba import *

with description('CryptogramProblem'):
  with it('ignores empty input'):
    expect(cryptogram_problem.CryptogramProblem.score([''])).to(equal(0))

  with it('rejects purely non-word inputs'):
    expect(cryptogram_problem.CryptogramProblem.score(['$#!7'])).to(equal(0))

  with it('favors jibberish'):
    expect(cryptogram_problem.CryptogramProblem.score([
      'asdf', 'fdsa', 'thesearenot', 'intest', 'dictionary',
    ])).to(equal(1))

  with it('accepts all other input'):
    expect(cryptogram_problem.CryptogramProblem.score(['owl'])).to(
        be_between(0, .25))

  with description('solutions'):
    with before.all:
      fixtures.init()

    with it('solves rot13'):
      p = cryptogram_problem.CryptogramProblem('rot13', ['bjy'])
      expect(p.solutions()).to(equal({'owl (rot13)': 1}))

    with it('solves rot14'):
      p = cryptogram_problem.CryptogramProblem('rot14', ['egbqdn'])
      expect(p.solutions()).to(equal({'superb (rot14)': 1}))

    with it('solves mixed rotN translations'):
      # bjy egbqdn
      # owl superb
      p = cryptogram_problem.CryptogramProblem('rot13 and 14', [
        'bjy egbqdn'
      ])
      expect(p.solutions()).to(equal({
        'owl rtodqa (rot13)': 1 / 3,
        'pxm superb (rot14)': 2 / 3,
      }))

    with it('solves ordinary cryptograms'):
      p = cryptogram_problem.CryptogramProblem('cryptogram', [
        # superb owl war plane snapshot scrapbook is now here.
        'fiune zlqg qbe ugbxn fxbufolv fkebuzllh pf xlq onen'
      ])
      solutions = p.solutions()
      expected = 'super bowl war plane snapshot scrapbook is now here'
      expect(solutions).to(have_key(expected))
      expect(solutions[expected]).to(be_above(0.5))

  with _description('real data'):
    with before.all:
      warehouse.save()
      prod_config.init()

    with after.all:
      prod_config.reset()
      warehouse.restore()

    with it('solves long cryptograms'):
      initial = """
        T gxawjhixtq om t jawe hz wkccde jrtj ghumomjm hz t mrhxj woege hz 
        eugxawjep jebj. Ieuextdda jre gowrex kmep jh eugxawj jre jebj om moqwde 
        euhkir jrtj jre gxawjhixtq gtu ve mhdnep va rtup. Zxefkeujda kmep txe 
        mkvmjojkjohu gowrexm lrexe etgr dejjex om xewdtgep va t pozzexeuj 
        dejjex hx ukqvex. Jh mhdne jre wkccde, hue qkmj xeghnex jre hxoioutd 
        dejjexoui. Jrhkir huge kmep ou qhxe mexohkm twwdogtjohum, jrea txe uhl 
        qtouda wxoujep zhx eujexjtouqeuj ou uelmwtwexm tup qtitcouem.
      """
      expected = """
        A cryptogram is a type of puzzle that consists of a short piece of 
        encrypted text. Generally the cipher used to encrypt the text is simple 
        enough that the cryptogram can be solved by hand. Frequently used are 
        substitution ciphers where each letter is replaced by a different 
        letter or number. To solve the puzzle, one must recover the original 
        lettering. Though once used in more serious applications, they are now 
        mainly printed for entertainment in newspapers and magazines.
      """
      p = cryptogram_problem.CryptogramProblem('large cryptogram', [initial])
      solutions = p.solutions()
      expect(solutions).to(have_key(expected))
      expect(solutions[expected]).to(be_above(0.9))

    with it('does not find solutions for long repeated strings'):
      p = cryptogram_problem.CryptogramProblem('large cryptogram', ['aaa'])
      expect(p.solutions()).to(be_empty)
