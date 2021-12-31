"""Parse a cryptic clue and find the "most probable" solution.

Broadly, find the "highest-scoring" interpretation which uses all given words.
A cryptic clue is one of:
```
  <word play> <definition>
  <definition> <word play>
```
Where `<word play>` is composed of indicators for shorthand ("energy" = "e"),
signals to anagram, look for homophones, etc.

For (approximately) each word in the clue, generators run which improve the path
through a graph of solutions. These generators expand the set of options until
future results are assumed to be worse than all existing results.
"""

from typing import List, Iterable, NamedTuple

from data import crossword, meta, warehouse, max_heap
from puzzle.problems.crossword import _cryptic_nodes


def parse(given: str) -> Iterable[_cryptic_nodes.Parsed]:
  plans = max_heap.MaxHeap()
  clue = _cryptic_nodes.Clue(given)
  words_api = warehouse.get('/api/words')
  definition = ''
  parsed = _cryptic_nodes._Node('asdf')
  result = _cryptic_nodes.Parsed(definition, parsed)
  yield result
  return
  for word in crossword.tokenize_clue(clue):
    words = meta.Meta()
    result.append(words)
    words[word] = 1
    base_form = words_api.base_form(word)
    if base_form != word:
      words[base_form] = min(0.9, len(base_form) / len(word))


def _anagram_iter(clue: _cryptic_nodes.Clue) -> Iterable[None]:
  return []
