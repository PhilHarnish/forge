from nltk.corpus import wordnet

from data import meta


def expand(word, pos=None):
  return synonyms(word, limit_one_word=True)


def synonyms(word, limit_one_word=True):
  suffix = _suffix(word)
  results = meta.Meta()
  visited = set()
  # Siblings.
  for synset in wordnet.synsets(word):
    _add_synset_lemmas(results, visited, synset, limit_one_word, suffix)
    # Children.
    for child in synset.hyponyms():
      _add_synset_lemmas(results, visited, child, limit_one_word, suffix)
    # Parents.
    for parent in synset.hypernyms():
      _add_synset_lemmas(results, visited, parent, limit_one_word, suffix)
  return results


def hypernyms(word, distance=2):
  results = meta.Meta()
  visited = set()
  suffix = _suffix(word)
  for synset in wordnet.synsets(word):
    _hypernyms(results, visited, synset, distance, suffix)
  return results


def _hypernyms(results, visited, synset, distance, suffix):
  if distance <= 0:
    return
  for parent in synset.hypernyms():
    _add_synset_lemmas(results, visited, parent, False, suffix)
    _hypernyms(results, visited, parent, distance - 1, suffix)


def _add_synset_lemmas(results, visited, synset, limit_one_word, suffix):
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
    if suffix:
      results[synonym_lemma + suffix] = 1


def _suffix(word):
  base_form = wordnet.morphy(word)
  if base_form is not None and base_form != word and word.startswith(base_form):
    # Only supports re-adding a removed suffix. Only works for some plurals.
    return word[len(base_form):]
  return ''
