from src.data import meta


class Trie(meta.Meta):
  def has_keys_with_prefix(self, prefix):
    return any([key.startswith(prefix) for key in self])

  def keys(self, prefix=''):
    if prefix:
      return [key for key in self if key.startswith(prefix)]
    return iter(self)
