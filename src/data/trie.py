import re

from src.data import meta


class Trie(meta.Meta):
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
    matcher = re.compile('^[%s]$' % ']['.join([
      ''.join(s) for s in seek_sets
    ]))
    return [(key, value) for key, value in self.items() if matcher.match(key)]
