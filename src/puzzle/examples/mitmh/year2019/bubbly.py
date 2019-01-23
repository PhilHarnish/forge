from typing import Dict, Tuple

bits = {
  c: 2**i for i, c in enumerate('abcdefghijklmnopqrstuvwxyz')
}
bits_to_chars = {
  v: k for k, v in bits.items()
}

_Relations = Dict[int, int]


def relate_binary(txt:str) -> Tuple[_Relations, int]:
  relations = {}
  remaining = 0
  mask = 0
  stack = [mask]
  for bubble in txt:
    for c in bubble:
      if c == ' ':
        mask = stack[-1]
      elif c == '(':
        stack.append(mask)
      elif c == ')':
        mask = stack.pop()
      else:
        bit = bits[c]
        remaining |= bit
        mask |= bit
        relations[bit] = mask
  if stack != [0]:
    raise IndexError('%s not balanced' % stack)
  return relations, remaining

def will_win_binary(
    relation: _Relations, remaining: int, cache: Dict[int, bool]=None
) -> bool:
  if cache is None:
    cache = {}
  elif remaining in cache:
    return cache[remaining]
  winning_moves = 0
  i = 1
  while i <= remaining:
    if remaining & i == 0:
      i *= 2
      continue
    child_round = remaining - (remaining & relation[i])
    if not child_round:
      # Removed everything this time.
      winning_moves += i
    elif not will_win_binary(relation, child_round, cache):
      # This alone did not lead to a win...
      # But opponent cannot force a win either.
      winning_moves += i
    # Loop remaining.
    i *= 2
  cache[remaining] = winning_moves
  return winning_moves

def char_dict(relations: _Relations) -> Dict[str, str]:
  result = {}
  for k, v in relations.items():
    result[bits_to_chars[k]] = chars(v)
  return result

def chars(binary: int) -> str:
  on = []
  for i, c in enumerate('abcdefghijklmnopqrstuvwxyz'):
    if binary & (2 ** i):
      on.append(c)
  return ''.join(on)
