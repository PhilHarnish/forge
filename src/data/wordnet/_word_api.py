from nltk.corpus import wordnet

from data import meta


def synonyms(word, limit_one_word=True):
  results = meta.Meta()
  visited = set()
  # Siblings.
  for synset in wordnet.synsets(word):
    _add_synset_lemmas(results, visited, synset, limit_one_word)
    # Parents.
    for parent in synset.hypernyms():
      _add_synset_lemmas(results, visited, parent, limit_one_word)
  return results


def hypernyms(word, distance=2):
  results = meta.Meta()
  visited = set()
  for synset in wordnet.synsets(word):
    _hypernyms(results, visited, synset, distance)
  return results


def _hypernyms(results, visited, synset, distance):
  if distance <= 0:
    return
  for parent in synset.hypernyms():
    _add_synset_lemmas(results, visited, parent, False)
    _hypernyms(results, visited, parent, distance - 1)


def _add_synset_lemmas(results, visited, synset, limit_one_word):
  if synset.name() in visited:
    return
  visited.add(synset.name())
  for synonym_lemma in synset.lemma_names():
    if synonym_lemma in results:
      continue
    elif '_' in synonym_lemma:
      if limit_one_word:
        continue
      synonym_lemma = synonym_lemma.replace('_', ' ')
    results[synonym_lemma] = 1
