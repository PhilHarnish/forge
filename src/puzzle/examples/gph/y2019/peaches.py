import collections
from typing import Callable, Iterable, List, Optional, Tuple

Mutations = Iterable[Tuple[str, Callable[[str], str]]]

# Set to force solution paths always require given string.
REQUIRED_SUBSTRING = ()

BOO_MAP = {
  'a': 'ue',
  'e': 'ai',
  'i': 'eo',
  'o': 'iu',
  'u': 'oa',
}
BOO_PRIME_SUCC_MAP = {  # Seeing a `key` requires `value` follows.
  leader: successor for (leader, successor) in BOO_MAP.values()
}
BOO_PRIME_LEAD_MAP = {  # Seeing a `key` implies insert `value`.
  value[0]: key for key, value in BOO_MAP.items()
}
LETTERS = 'zabcdefghijklmnopqrstuvwxyza'
# Override available letters, if appropriate:
# LETTERS = 'asinrd'
WIGGLER_MAP = {
  LETTERS[i]: LETTERS[i+1] + LETTERS[i-1] for i in range(1, len(LETTERS) - 1)
}
# Override available wiggler moves, if appropriate:
# WIGGLER_MAP = {'n': 'om', 'e': 'fd'}
WIGGLER_PRIME_SUCC_MAP = {
  leader: successor for (leader, successor) in WIGGLER_MAP.values()
}
WIGGLER_PRIME_LEAD_MAP = {
  value[0]: key for key, value in WIGGLER_MAP.items()
}

SHYGUY_MAP = str.maketrans('lr', 'rl')


def boo(a: str) -> str:
  return ''.join(BOO_MAP.get(c, c) for c in a)

def BOO(src: str, acc: tuple) -> Mutations:
  del src, acc
  yield 'boo', boo

def boo_prime(src: str) -> str:
  i = 0
  end = len(src)
  result = []
  while i < end:
    c = src[i]
    result.append(BOO_PRIME_LEAD_MAP.get(c, c))
    if src[i] in BOO_PRIME_SUCC_MAP:
      i += 1  # Skip next letter.
    i += 1
  return ''.join(result)

def BOO_PRIME(src: str, acc: tuple) -> Mutations:
  del acc
  i = 0
  end = len(src) - 1
  while i < end:
    if src[i] in BOO_PRIME_SUCC_MAP:
      if BOO_PRIME_SUCC_MAP[src[i]] != src[i+1]:
        return
      i += 1  # Skip the pair.
    i += 1
  # Special case for last letter which may have been unchecked.
  if src[-1] in BOO_PRIME_SUCC_MAP and src[-2] not in BOO_PRIME_SUCC_MAP:
    return
  yield 'boo', boo_prime

def bowser(a: str) -> str:
  lowest_c = min(a)
  return a.replace(lowest_c, '')

def BOWSER(src: str, acc: tuple) -> Mutations:
  if any_dupe('bowser', acc):
    return
  del src, acc
  yield 'bowser', bowser

def bullet(a: str, charge:str) -> str:
  return charge[0] + a[1:]

def BULLET(src: str, acc: tuple) -> Mutations:
  del src
  if next_dupe('bullet', acc):
    return
  for c in LETTERS:
    yield 'bullet(%s)' % c, lambda a: bullet(a, c)

BULLET_PRIME = BULLET

def inky(a: str, charge:str) -> str:
  return a[0] + charge[0] + a[1:-1] + charge[0] + a[-1]

def INKY(src: str, acc: tuple) -> Mutations:
  del src, acc
  for c in LETTERS:
    yield 'inky(%s)' % c, lambda a: inky(a, c)

def inky_prime(src: str) -> str:
  return src[0] + src[2:-2] + src[-1]

def INKY_PRIME(src: str, acc: tuple) -> Mutations:
  del acc
  if len(src) < 4:
    return
  if src[1] != src[-2]:
    return
  yield 'inky(%s)' % src[1], inky_prime

def lakitu(a: str, n:int) -> str:
  return a[n:] + a[:n]

def LAKITU(src: str, acc: tuple) -> Mutations:
  if next_dupe('lakitu', acc):
    return
  for n in range(1, len(src)):
    yield 'lakitu(%s)' % src[n], lambda a: lakitu(a, n)

LAKITU_PRIME = LAKITU

def piranha(a: str) -> str:
  n = int(len(a) / 2)
  return a[n:] + ' ' + a[:n]

def PIRANHA(src: str, acc: tuple) -> Mutations:
  del acc
  if ' ' in src:  # Limit to 1 word.
    return
  yield 'piranha', piranha

def shyguy(a: str) -> str:
  return a.translate(SHYGUY_MAP)

def SHYGUY(src: str, acc: tuple) -> Mutations:
  del src
  if next_dupe('shyguy', acc):
    return
  yield 'shyguy', shyguy

def wiggler(a: str, n: int) -> str:
  return a[:n] + WIGGLER_MAP[a[n]] + a[n + 1:]

def WIGGLER(src: str, acc: tuple) -> Mutations:
  del acc
  for n in range(len(src) - 1):
    if src[n] in WIGGLER_MAP:
      yield 'wiggler(%s%d)' % (src[n], n), lambda a: wiggler(a, n)

def wiggler_prime(src: str, n: int) -> str:
  return src[:n] + WIGGLER_PRIME_LEAD_MAP[src[n]] + src[n+2:]

def WIGGLER_PRIME(src: str, acc: tuple) -> Mutations:
  del acc
  i = 0
  end = len(src) - 1
  while i < end:
    if src[i] in WIGGLER_PRIME_SUCC_MAP:
      if WIGGLER_PRIME_SUCC_MAP[src[i]] == src[i+1]:
        yield 'wiggler(%s%d)' % (src[i], i), lambda a: wiggler_prime(a, i)
        i += 1  # Skip the pair.
    i += 1


CAN_SHRINK = {
  BOWSER,
  BOO_PRIME,
  WIGGLER_PRIME,
  INKY_PRIME,
}
CAN_GROW = {
  BOO,
  WIGGLER,
  INKY,
  PIRANHA,
}


def search(start: str, end: str, characters: list) -> str:
  result = search_inner(start, end, characters)
  formatted = []
  while result:
    result, top = result
    formatted.append(top)
  return ', '.join(reversed(formatted))


def search_inner(
    start: str, end: str, characters: list, depth: int = 10) -> Optional[tuple]:
  queue = collections.deque([(start, (), depth)])
  end_length = len(end)
  can_shrink = any(c in CAN_SHRINK for c in characters)
  can_grow = any(c in CAN_GROW for c in characters)
  last_depth = None
  seen = set()
  while queue:
    current, acc, remaining = queue.popleft()
    if last_depth != remaining:
      last_depth = remaining
      print('depth = %s; len = %s' % (remaining, len(queue)))
    if remaining <= 0:
      continue
    for desc, mutation in mutations(characters, current, acc):
      changed = mutation(current).strip()
      if changed == end:
        return acc, desc
      elif remaining <= 0:
        continue
      elif changed != start:
        changed_length = len(changed)
        if (
            (changed_length == end_length) or
            (changed_length > end_length and can_shrink) or
            can_grow
          ):
          if any(s not in changed+changed for s in REQUIRED_SUBSTRING):
            continue
          hashed = hash(changed)
          if hashed not in seen:
            seen.add(hashed)  # Never revisit same word twice.
            queue.append((changed, (acc, desc), remaining - 1))
  return None

def mutations(characters: List[Callable], src: str, acc: tuple) -> Iterable:
  for character in characters:
    yield from character(src, acc)


def next_dupe(search: str, acc: tuple):
  if not acc:
    return False
  return acc[1].startswith(search)

def any_dupe(search: str, acc: tuple):
  while acc:
    if acc[1].startswith(search):
      return True
    acc = acc[0]
  return False
