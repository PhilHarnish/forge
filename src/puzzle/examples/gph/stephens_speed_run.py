paths = [
  'LDRLDLRDUURULDDDRLLUULUDRDLRRD',  # level "1".
  'UDLLDDRUDDRRRRDUURUULLUURLULDRUDLLDRRUUR',  # level "2".
  'UUULRUULRRURRRUDRDLUULLLLLUDRDLLDDDDDRRRRRUULDDLLLLLDU',  # level "3".
  # level "4"; looks like '21'.
  'LDDRLDLLDULURDDRRRDULRDUURULUDLUDRLDDLLURRDURRDURUDL',
  # level "5"; top (of 2) sausage is unreachable.
  'DRDLLULRDURURLULRU',
  # level "6"; 1 sausage with grill to left of it.
  'UULLUDRDDDLLURRDULRDRUULRDRULLDURLRUDD',
  # level "7"; - goes right, | goes left.
  'LDULUURRRDRUDRDDLLLUURUDLRRURULL',
  # level "8"; horz strip.
  'RULDLRRURRRUDRDDLUUURLLLULLLDLRURDRL',
  # level "9"; |__:.
  'DUDLLULRDRUUULRURLLUDDLDRRUL',
]

codes = [27, 16, 30, 34, 55, 46, 49, 37, 63]

assert (len(paths) == len(codes))

for i, path in enumerate(paths):
  print(''.join(
      [chr(len(path) + codes[i] + offset) for offset in range(-6, 1)]))
