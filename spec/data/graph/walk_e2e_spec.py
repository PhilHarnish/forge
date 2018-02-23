from data import pickle_cache, word_frequencies
from data.graph import bloom_node, regex, trie, walk
from spec.mamba import *

_FIRST_WORD_WEIGHT = 23135851162


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
    if multi:
      if not all(_check(word) for word in line.split()):
        continue
    elif not _check(line):
      continue
    yield line, value


def make_trie(length_mask) -> bloom_node.BloomNode:
  root = bloom_node.BloomNode()
  for word, value in get_words(length_mask=length_mask):
    trie.add(root, word, value / _FIRST_WORD_WEIGHT)
  return root


@pickle_cache.cache('data/graph/walk_e2e_spec/trie')
def pickled_trie(length_mask: int) -> bloom_node.BloomNode:
  return make_trie(length_mask)


@pickle_cache.cache('data/graph/walk_e2e_spec/ngrams')
def pickled_ngrams(length_mask: int) -> bloom_node.BloomNode:
  ngrams = [list(get_words(length_mask=length_mask))]
  for i in range(2, 5+1):
    ngrams.append(list(get_words(
        length_mask=length_mask, file='data/coca_%sgram.txt' % i, multi=True)))
  root = bloom_node.BloomNode()
  trie.add_ngrams(root, ngrams)
  return root


def results(root) -> List[str]:
  results = []
  for word, _ in walk.walk(root):
    results.append(word)
  return results


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


with description('benchmarks: trie creation', 'end2end'):
  with it('creates unigram trie'):
    with benchmark(1030) as should_run:
      if should_run:
        root = make_trie(0b111111110)
        expect(repr(root)).to(equal(
            "BloomNode('abcdefghijklmnopqrstuvwxyz', ' ########', 0)"))

  with it('creates unigram + bigram trie'):
    with benchmark(7000) as should_run:
      if should_run:
        unigrams = list(get_words())
        bigrams = list(get_words(file='data/count_2w_aggregated.txt'))
        root = bloom_node.BloomNode()
        trie.add_ngrams(root, [unigrams, bigrams])
        expect(path(root, 'to be a')).to(equal([
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', ' ############', 0)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', '############', 6.867071358893854e-06)",
          "BloomNode('abcdefghiklmnopqrstuvwxyz; ', '###########', 0.0004906526796536196)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', ' ############', 0)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', '############', 1.8976823503140278e-07)",
          "BloomNode('abcdefghiklmnopqrstuvwxyz; ', '###########', 1.313779931343778e-05)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', ' ############', 0)",
          "BloomNode('abcdefghijklmnopqrstuvwxyz; ', '############', 4.709283276142498e-06)"
        ]))

with description('benchmarks: node merging', 'end2end') as self:
  with before.all:
    self.root = pickled_trie(1 << 7)
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
    #self.root = ngram.get(lengths_mask=0b111111)
    self.root = pickled_ngrams(0b111111)

  with it('should find common results'):
    words = []
    for word, _ in walk.walk(self.root):
      words.append(word)
      if len(words) > 10:
        break
    expect(words).to(equal([
      'the', 'and', 'that', 'the the', 'a the', 'an the', 'and the', 'that the',
      'for', 'for the', 'was'
    ]))

  with it('should find explicit solutions'):
    merged = self.root * regex.parse('plums of wrath')
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
