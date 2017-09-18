def str_to_str(input, str_map):
  yield from _str_to_str(input, str_map, [])

def _str_to_str(input, str_map, acc):
  for prefix, replacements in str_map.items():
    if not input.startswith(prefix):
      continue
    for replacement in replacements:
      acc.append(replacement)
      yield from _str_to_str(input[len(prefix):], str_map, acc)
      acc.pop()
  if not input:
    yield ''.join(acc)
