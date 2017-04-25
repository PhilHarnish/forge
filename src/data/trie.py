import collections
import functools
import re


class Trie(collections.OrderedDict):
  def __init__(self, data):
    self._smallest = float('inf')
    super(Trie, self).__init__(data)

  def __setitem__(self, key, value, *args, **kwargs):
    if value > self._smallest:
      raise AssertionError('Items must be added to trie in descending order.')
    else:
      self._smallest = value
    super(Trie, self).__setitem__(key, value, *args, **kwargs)


  def has_keys_with_prefix(self, prefix):
    return any([key.startswith(prefix) for key in self])

  def keys(self, prefix=''):
    if prefix:
      return [key for key in self if key.startswith(prefix)]
    return iter(self)

  def items(self, prefix=None, seek=None):
    result = super(Trie, self).items()
    if not seek:
      if prefix:
        return [kvp for kvp in result if kvp[0].startswith(prefix)]
      return result
    l = len(prefix)
    return [
      (key, weight) for key, weight in result if key.startswith(prefix) and (
          len(key) < l or key[l] in seek)
    ]

  def walk(self, seek_sets):
    """Returns solutions matching `seek_sets`, ordered from high to low."""
    # Convert seek_sets into a regular expression.
    matcher = _regexp(seek_sets)
    return [(key, value) for key, value in self.items() if matcher.match(key)]

functools.lru_cache(maxsize=1)
def _regexp(seek_sets):
  return re.compile(''.join([
    '^',
    '[%s]' % ''.join(seek_sets[0]),
  ] + [
    '($|[%s])' % ''.join(s) for s in seek_sets[1:]
  ] + [
    '$'
  ]))
