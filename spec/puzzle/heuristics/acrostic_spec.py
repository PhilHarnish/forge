from data import warehouse, word_frequencies
from puzzle.heuristics import acrostic
from puzzle.puzzlepedia import prod_config
from spec.mamba import *

BA_PREFIX_TRIE = word_frequencies.load(
    zip(('bad', 'bag', 'ban', 'bar', 'bat'), [1]*5))

with description('acrostic'):
  with it('uses a mock trie'):
    a = acrostic.Acrostic(list('bag'), BA_PREFIX_TRIE)
    expect(len(a._trie)).to(be_below(100))

  with it('yields multi-character solutions'):
    a = acrostic.Acrostic(list('bag'), BA_PREFIX_TRIE)
    expect(list(a)).to(contain('bag'))

  with it('is observable'):
    a = acrostic.Acrostic(list('bag'), BA_PREFIX_TRIE)
    subs = mock.Mock()
    a.subscribe(subs)
    expect(subs.on_next.call_args).to(equal(mock.call('bag')))

  with it('yields unique solutions'):
    a = acrostic.Acrostic(list('ba') + ['ggg'], BA_PREFIX_TRIE)
    expect(list(a)).to(have_len(1))

  with it('yields multiple multi-character solutions'):
    a = acrostic.Acrostic(list('ba') + ['dgnrt'], BA_PREFIX_TRIE)
    expect(list(a)).to(contain('bad', 'bag', 'ban', 'bar', 'bat'))

  with description('real data'):
    with before.all:
      warehouse.save()
      prod_config.init()

    with after.all:
      prod_config.reset()
      warehouse.restore()

    with it('finds simple words'):
      a = acrostic.Acrostic('cab')
      expected = [
        'cab',
        'ca b',
        'c ab',
      ]
      for i, (answer, weight) in enumerate(a.items()):
        expect('#%s = %s @ %s' % (i, answer, weight)).to(equal(
            '#%s = %s @ %s' % (i, expected[i], weight)
        ))
      expect(a.items()).to(have_len(len(expected)))

    with it('finds important words'):
      a = acrostic.Acrostic('binary')
      expect(next(a.items())).to(equal(('binary', 1)))

    with _it('modestly expensive'):
      words = [
        'larch', 'simple', 'foray', 'doyen', 'eerily', 'soup', 'must',
      ]
      a = acrostic.Acrostic(words)
      limit = 1000000
      for i, (answer, weight) in enumerate(a.items()):
        if answer.startswith('answer') or i % 1000 == 0:
          print(answer, weight)
        if i > limit:
          print('tried %s' % i)
          break

    with _it('crazy expensive'):
      words = [
        'champion', 'nitpick', 'conspiracy', 'windpipe', 'epinephrine',
        'philanthropic', 'sierpinski', 'mississippi', 'pilaf', 'vulpine',
        'spinach', 'pinochet', 'porcupine', 'megapixels', 'australopithecus',
        'sharpie', 'intrepid', 'insipid', 'robespierre'
      ]
      a = acrostic.Acrostic(words)
      limit = 1000000
      for i, (answer, weight) in enumerate(a.items()):
        if answer.startswith('answer') or i % (limit / 10) == 0:
          print(answer, weight)
        if i > limit:
          print('tried %s' % i)
          break
      """ 4/24
      a to incipient each rss 120548796
      a to incipient opps eii 153396
      a to incipient eipe rni 59329
      a to incipient ipps epe 174519
      a to incipient cmss ede 290375
      a to incipient csts rsr 175192
      a to incipient opca dsr 752124
      a to incipient cisr tnp 87249
      a to incipient ilos dps 1290835
      a to pntemplates cs tio 770193
      a to perempuan usps tio 770193

      4/25 + early break in walk when scores are low
      a to incipient each rss 120548796
      a to incipient iste eie 57198
      a to incipient cmss dss 1995347
      a to incipient imia rsi 697477
      a to incipient osrs eip 398559
      a to perempuan peas tpe 275152
      a to perempuan imcs nss 990710
      a to perempuan caar ens 717319
      a to perempuan usea tns 523866
      a to perempuan epra pii 512601
      a to dicipline imps psi 6101411
      
      9/15 38 seconds; 35 seconds
      a to incipient usui ipi 1.699863585947228e-07
      a in incipient isps psr 3.399727171894456e-07
      a in incipient rire dns 5.7795361922205745e-06
      a i applesauce isls pdo 1.699863585947228e-07
      a i applesauce pirs inr 6.799454343788912e-07
      a i renaisance csus iss 2.209822661731396e-06
      a i renaisance cmaa nsp 3.399727171894456e-07
      a i renassance imes nss 5.099590757841683e-07
      a can eliminate aisi ds 3.399727171894456e-07
      a can eliminate phr dio 1.699863585947228e-07
      """
