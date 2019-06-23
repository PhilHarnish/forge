from puzzle.examples.gph.y2019 import peaches
from spec.mamba import *

with _description('peaches') as self:
  with description('boo'):
    with it('unagi -> ungi'):
      expect(peaches.boo('turf')).to(equal('toarf'))

  with description('bowser'):
    with it('unagi -> ungi'):
      expect(peaches.bowser('unagi')).to(equal('ungi'))

    with it('reef -> rf'):
      expect(peaches.bowser('reef')).to(equal('rf'))

  with description('bullet'):
    with it('turf -> durf'):
      expect(peaches.bullet('turf', 'd')).to(equal('durf'))

  with description('inky'):
    with it('hay -> hlaly'):
      expect(peaches.inky('hay', 'l')).to(equal('hlaly'))

  with description('lakitu'):
    with it('turf -> urft'):
      expect(peaches.lakitu('turf', 1)).to(equal('urft'))

  with description('piranha'):
    with it('hay -> ay h'):
      expect(peaches.piranha('hay')).to(equal('ay h'))

    with it('igay -> ay ig'):
      expect(peaches.piranha('igay')).to(equal('ay ig'))

  with description('shyguy'):
    with it('hay -> hay'):
      expect(peaches.shyguy('hay')).to(equal('hay'))

    with it('hlaly -> hrary'):
      expect(peaches.shyguy('hlaly')).to(equal('hrary'))

  with description('wiggler'):
    with it('turf -> tvtrf'):
      expect(peaches.wiggler('turf', 1)).to(equal('tvtrf'))

  with description('backwards'):
    with it('rejects invalid boos'):
      expect(peaches.BOO_PRIME('abs', ())).to(have_len(0))
      expect(peaches.BOO_PRIME('bsa', ())).to(have_len(0))

    with it('accepts valid boos'):
      expect(calling(peaches.BOO_PRIME, 'toarf', ())).to(have_len(1))
      expect(calling(peaches.BOO_PRIME, 'ueaieoiuoa', ())).to(have_len(1))

    with it('performs reverse boos'):
      expect(peaches.boo_prime('toarf')).to(equal('turf'))
      expect(peaches.boo_prime('ueaieoiuoa')).to(equal('aeiou'))

    with it('rejects invalid inkys'):
      expect(peaches.INKY_PRIME('aba', ())).to(have_len(0))
      expect(peaches.INKY_PRIME('asdf', ())).to(have_len(0))

    with it('accepts valid inkys'):
      expect(calling(peaches.INKY_PRIME, 'reef', ())).to(have_len(1))
      expect(calling(peaches.INKY_PRIME, 'weatreel', ())).to(have_len(1))

    with it('performs reverse inkys'):
      expect(peaches.inky_prime('reef')).to(equal('rf'))
      expect(peaches.inky_prime('weatreel')).to(equal('watrel'))

    with it('rejects invalid wiggler'):
      expect(peaches.WIGGLER_PRIME('aba', ())).to(have_len(0))
      expect(peaches.WIGGLER_PRIME('asdf', ())).to(have_len(0))

    with it('accepts valid wiggler'):
      expect(calling(peaches.WIGGLER_PRIME, 'ca', ())).to(have_len(1))
      expect(calling(peaches.WIGGLER_PRIME, 'tpnarf', ())).to(have_len(1))

    with it('performs reverse wiggler'):
      expect(peaches.wiggler_prime('ca', 0)).to(equal('b'))
      expect(peaches.wiggler_prime('tpnarf', 1)).to(equal('toarf'))

  with description('search end2end', 'end2end'):
    with it('finds turf -> urft'):
      expect(peaches.search('turf', 'urft', [
        peaches.BULLET,
        peaches.BOO,
        peaches.WIGGLER,
        peaches.LAKITU,
      ])).to(equal('lakitu(u)'))

    with _it('finds hay -> candy hen'):
      expect(peaches.search('hay', 'candy hen', [
        peaches.SHYGUY,
        peaches.WIGGLER,
        peaches.PIRANHA,
        peaches.INKY,
        peaches.LAKITU,
      ])).to(equal(
          'inky(d), wiggler(d1), piranha, inky(n), lakitu(c)'))

    with _it('finds turf -> parfait'):
      expect(peaches.search('turf', 'parfait', [
        peaches.BULLET,
        peaches.BOO,
        peaches.WIGGLER,
        peaches.LAKITU,
      ])).to(equal(
          'bullet(u), wiggler(u0), bullet(e), boo, lakitu(o), bullet(p)'))

    with _it('finds heron -> onigiri'):
      expect(peaches.search('heron', 'onigiri', [
        peaches.BULLET,
        peaches.BOO,
        peaches.WIGGLER,
        peaches.LAKITU,
      ])).to(equal('???'))

    with _it('finds easel -> water eel'):
      expect(peaches.search('easel', 'water eel', [
        peaches.BULLET,
        peaches.WIGGLER,
        peaches.PIRANHA,
        peaches.INKY,
        peaches.LAKITU,
      ])).to(equal('???'))

    with _it('finds dress -> tons of noodles'):
      expect(peaches.search('tons of noodles', 'dless', [
        peaches.BULLET,
        peaches.PIRANHA,
        peaches.INKY,
        peaches.LAKITU,
      ])).to(equal('???'))

    with _it('finds shrine -> refreshroom'):
      expect(peaches.search('shrine', 'refreshroom', [
        peaches.BOWSER,
        #peaches.SHYGUY,
        peaches.BOO,
        peaches.WIGGLER,
        peaches.INKY,
        peaches.LAKITU,
      ])).to(equal('???'))

    with _it('finds reversed asian squid -> snow'):
      expect(peaches.search('ruidasian', 'sniuw', [
        peaches.BULLET_PRIME,
        peaches.INKY_PRIME,
        peaches.LAKITU_PRIME,
      ])).to(equal('???'))

    with _it('finds reversed asian squid -> snow'):
      expect(peaches.search('sniuw', 'ruidasian', [
        peaches.BULLET,
        peaches.INKY,
        peaches.LAKITU,
      ])).to(equal('???'))

    with _it('finds demon -> lemon eggnog'):
      expect(peaches.search('demon', 'eggnoglemon', [
        peaches.BULLET,
        #peaches.PIRANHA,
        peaches.INKY,
        peaches.LAKITU,
      ])).to(equal('???'))
