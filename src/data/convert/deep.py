def lower(o):
  t = type(o)
  if t == str:
    return o.lower()
  elif t in (list, tuple, set):
    return t(lower(i) for i in o)
  elif t == dict:
    return dict((lower(k), lower(v)) for k, v in o.items())
  raise TypeError('Unable to lower %s (%s)' % (o, repr(o)))
