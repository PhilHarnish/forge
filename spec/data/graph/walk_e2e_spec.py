from data import word_frequencies
from data.graph import bloom_node, ngram, regex, walk
from spec.mamba import *


def get_words(
    length_mask: int = None,
    file: str = 'data/g1m_1gram.txt',
    multi: bool = False) -> list:
  def _check(word: str) -> bool:
    if not word.isalpha():
      return False
    if length_mask and (1 << len(word)) & length_mask == 0:
      return False
    return True
  for line, value in word_frequencies.parse_file(file):
    if len(line) > 12:
      continue
    if multi and not all(_check(word) for word in line.split()):
      continue
    elif not _check(line):
      continue
    yield line, value


def pickled_ngrams(length_mask: int) -> bloom_node.BloomNode:
  return ngram.get(lengths_mask=length_mask)


def results(root) -> List[str]:
  return [w for w, _ in walk.walk(root)]


def path(root: bloom_node.BloomNode, path: str) -> List[str]:
  result = []
  cursor = root
  for c in path:
    result.append(repr(cursor))
    cursor = cursor[c]
  result.append(repr(cursor))
  return result


def head2head(patterns, trie, words) -> tuple:
  start = time.time()
  merged = trie
  for pattern in patterns:
    merged *= regex.parse(pattern)
  actual = results(merged)
  trie_elapsed = time.time() - start
  start = time.time()
  expressions = [re.compile('^%s$' % pattern) for pattern in patterns]
  expected = [
    word for word, _ in words if all(re.match(exp, word) for exp in expressions)
  ]
  re_elapsed = time.time() - start
  print('trie %.2fx faster for %s' % (re_elapsed / trie_elapsed, patterns))
  return expected, actual


with description('benchmarks: node merging', 'end2end') as self:
  with before.all:
    self.root = pickled_ngrams(1 << 7)
    self.words = list(get_words())

  with it('finds nodes matching .e.k.n.'):
    expected, actual = head2head(['.e.k.n.'], self.root, self.words)
    expect(actual).to(equal(expected))

  with it('finds nodes matching s.e.i.g'):
    expected, actual = head2head(['s.e.i.g'], self.root, self.words)
    expect(actual).to(equal(expected))

  with it('finds nodes matching multiple regular expressions'):
    expected, actual = head2head(['s.e.i.g', '.e.k.n.'], self.root, self.words)
    expect(actual).to(equal(expected))
    expect(actual).to(equal(['seeking']))

  with it('finds nodes for expensive queries'):
    expected, actual = head2head([
      '...alls',
    ], self.root, self.words)
    expect(actual).to(equal(expected))
    expect(actual).to(equal(['recalls', 'befalls']))

  with it('finds nodes for very expensive queries'):
    expected, actual = head2head([
      '.......',
      '...a...',
      '....l..',
      '.....l.',
      '......s',
    ], self.root, self.words)
    expect(expected).to(equal(actual))
    expect(actual).to(equal(['recalls', 'befalls']))


with description('benchmarks: unigram/bigram walk', 'end2end') as self:
  with before.all:
    self.root = pickled_ngrams(0b111111)

  with it('should find common results'):
    words = []
    for word, _ in walk.walk(self.root):
      words.append(word)
      if len(words) > 10:
        break
    expect(words).to(equal([
      'the', 'and', 'that', 'for', 'was', 'with', 'are', 'not', 'from', 'his',
      'have'
    ]))

  with it('should find explicit solutions'):
    merged = self.root * regex.parse('plums of wrath')
    expect(path_values(merged, 'plums of wrath')).to(look_like("""
      BloomNode('LMPSU; !', '     #', 0)
      p = BloomNode('LMSU; !', '    #', 0)
      l = BloomNode('MSU; !', '   #', 0)
      u = BloomNode('MS; !', '  #', 0)
      m = BloomNode('S; !', ' #', 0)
      s = BloomNode(' !', '#', 0)
        = BloomNode('FO; !', '  #', 0)
      o = BloomNode('F; !', ' #', 0)
      f = BloomNode(' !', '#', 0)
        = BloomNode('AHRTW', '     #', 0)
      w = BloomNode('AHRT', '    #', 0)
      r = BloomNode('AHT', '   #', 0)
      a = BloomNode('HT', '  #', 0)
      t = BloomNode('H', ' #', 0)
      h = BloomNode(' !', '#', 0.05183982849121094)
    """))
    expect(results(merged)).to(equal(['plums of wrath']))

  with it('should find constrained solutions'):
    expression = ' '.join([
      '[lump][threadle][deus][rhumb][shopping]',  # plums
      '[ok][frow]',  # of
      '[wed][caret][again][toque][hon]',  # wrath
    ])
    merged = self.root * regex.parse(expression)
    expect(results(merged)).to(contain('plums of wrath'))

  with it('should terminate for difficult expression'):
    merged = self.root * regex.parse('{super bowl}')
    expect(results(merged)).to(contain(
        'blow super', 'blow purse', 'pulse brow', 'pure blows', 'pure bowls',
        'blue prows', 'blows pure', 'spur below', 'purse blow', 'super blow',
        'super bowl', 'bowl super'))

  with it('should find long anagram patterns'):
    merged = self.root * regex.parse('{sup..}')
    x = results(merged)
    expect(results(merged)).to(contain(
        'pulse', 'upset', 'pause', 'pious', 'super', 'purse', 'setup', 'pumps',
        'pulls', 'syrup', 'jumps', 'stump', 'pours', 'plugs', 'lumps', 'slump',
        'pouts', 'sumps', 'spuds', 'punts', 'pumas', 'burps', 'stoup', 'pucks',
    ))

  with it('should sanely tokenize ambiguous strings #1'):
    root = pickled_ngrams(0b1011000)
    merged = root * regex.parse(' ?'.join('bannedperandsign'))
    expect(next(walk.walk(merged))[0]).to(equal('banned per and sign'))

  with it('should sanely tokenize ambiguous strings #2'):
    root = pickled_ngrams(0b110001100)
    merged = root * regex.parse(' ?'.join('enjoyedandorsimulate'))
    expect(next(walk.walk(merged))[0]).to(equal('enjoyed and or simulate'))
