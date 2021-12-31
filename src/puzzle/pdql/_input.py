class _InputMixin(object):
  def input(self, *args, **kwargs):
    for i in args:
      if isinstance(i, list):
        pass
