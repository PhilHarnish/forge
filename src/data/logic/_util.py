import ast


def parse(address):
  result = {}
  for subscript in address.split('.'):
    key, value_str = subscript.rstrip(']').split('[')
    value = ast.literal_eval(value_str)
    result[key] = value
  return result


def combine(a, b):
  combined = a.copy()
  for key, value in b.items():
    if key not in combined or combined[key] is None:
      combined[key] = value
    elif value is None:
      pass  # combined already has a more specific version of key.
    elif combined[key] != value:
      raise KeyError('%s is over constrained (both %s and %s)' % (
        key, combined[key], value,
      ))
  return combined
