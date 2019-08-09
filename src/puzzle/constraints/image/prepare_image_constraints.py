from typing import Optional

from puzzle.constraints import constraints, validator

_DEPS = {
  'crop': {'normalize'},
  'enhance': {'grayscale', 'invert', 'normalize'},
  'grayscale': {'normalize'},
}


class PrepareImageConstraints(constraints.Constraints):
  normalize: bool = True
  invert: bool = True
  crop: Optional[validator.NumberInRange(min_value=0, max_value=255)] = 0
  grayscale: bool = True
  enhance: bool = True

  def is_modifiable(self, key: str) -> bool:
    value = getattr(self, key)
    if value:
      # `key` can only be made False if all dependencies are also False.
      return all(self._key_in_dep_falsifiable(key, dep) for dep in _DEPS)
    if key in _DEPS:
      # `key` can only be made True if all of it's own dependencies are True.
      return all(getattr(self, dep) for dep in _DEPS[key])
    return super(PrepareImageConstraints, self).is_modifiable(key)

  def _key_in_dep_falsifiable(self, key: str, dep: str) -> bool:
    return (key not in _DEPS[dep] or  # Irrelevant.
            getattr(self, dep) is None or  # Cleared.
            getattr(self, dep) is False)  # Off.
