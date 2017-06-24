class _DimensionFactory(object):
  def __init__(self):
    self._dimensions = {}

  def __call__(self, *args, **kwargs):
    if not kwargs:
      raise TypeError('kwarg is required')
    elif len(kwargs) > 1:
      raise TypeError('Register only one dimension at a time (%s given)' % (
        ', '.join(kwargs.keys())))
    for key, value in kwargs.items():
      if key in self._dimensions:
        raise TypeError('Dimension %s already registered to %s' % (
          key, self._dimensions[key]
        ))
      self._dimensions[key] = value
      return value
    raise TypeError('invalid call %s %s' % (args, kwargs))
