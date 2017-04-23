import networkx

from src.puzzle.heuristics import acrostic

class _AcrosticGraph(acrostic.Acrostic):
  """Model for list of words and random walks through those words.

  Some notes on complexity:
    (where n = number of words, m = max length of words, N = last word)
  * The characters in word are nodes in a weighted directed acyclic graph.
  * Duplicate characters in a word can be ignored.
  * Weights are drawn from Trie predicted next-character frequencies.
  * Characters in word[i] have a directed edge to characters in word[i+1]...
    * ...only if the edge continues a prefix for another word and/or...
    * ...completes a word.
  * If word[i] -> word[i+1] completes a word then that edge leads to a new graph
    where all incoming edges are word completions from other n-length paths.
  * There are O(n*m) trees because:
    * Every len(word[i+1]) may start a new phrase with max len(words)-1
      characters in the output phrase.
    * However, since a new phrase does not have previous history there are
      O(n*m) many phrase-start trees. I.e., all paths to a phrase-start tree
      of a given length L complete an L-length word and lead to the same set of
      phrase start trees.
  * There are O(m^(n^2+n)) total nodes:
    * There are len(word[N]) = O(m) phrase-start sub-trees at word[N].
    * There are O(m) phrase-start trees at word[N-1] each leading to O(m) more
      trees for 2 length words and leading to previous O(m) more trees for
      two 1 length words. For two layers, this totals to m + m*m = O(m^2).
    * This continues up the tree like so:
      m + m*m + m*m*m + ... + m^n =
      m^1 + m^2 + m^3 + ... + m^n =
      -> 1 + 2 + 3 + ... + n = (n^2 + n)/2
      ...for a total of O(m^(n^2+n)) total nodes.
  * The number of edges is... somewhat higher and left as an exercise to the
    reader.
  * Completed words combine to form a new weighted directed acyclic graph
    composed of "phrases" whose edge weights are drawn from bi-gram frequencies.
  * I.e.: all paths <start> -> word[1] -> ... word[n] -> <end> makes M phrases.
  * ...and all paths <start> -> phrase[1] -> ... phrase[m] -> <end> makes
    solutions.
  """

  def __init__(self, words, trie=None):
    super(_AcrosticGraph, self).__init__(words, trie)
    g = _Graph()
    last = '^'
    for word in self._words:
      for a in last:
        for b in word:
          g.add_edge(a, b, weight=1)
      last = word
    for c in last:
      g.add_edge(c, '$', weight=0)
    self._graph = g

  def __iter__(self):
    for path in networkx.shortest_simple_paths(self._graph, '^', '$', 'weight'):
      result = []
      for node in path:
        if node == '^':
          continue
        elif node == '$':
          yield ''.join(result)
        else:
          result.append(node)

  def cost(self):
    return self._graph.number_of_edges()

class _Graph(networkx.DiGraph):
  """Model object for all nodes and edges in a graph.

  Node naming convention:
  - self['a'] is a node which starts phrases which begin with prefix "a".
    These phrases have length N, the number of words.
  - self['ai'] is likewise a node which starts phrases beginning with "ai".
    These also have length N.
  - self['_i'] is a node which starts all N-1 length phrases.
  - self['a']['ai'] is an edge from a -> ai.
  - self['ai']['aid'] is an edge from ai -> aid.
  - ('a', 'ai', 'aid') is a path from a -> ai -> aid = "aid".
  - ('a', '_i', '_id') is a path from a -> _i -> _id = "a id".
  """
  pass
