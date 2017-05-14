ALPHABET = [
  ' ',  # 0: ⠀ </>
  'a',  # 1: ⠁ 1
  None,  # 2: ⠂ 2
  'c',  # 3: ⠃ 12
  ',',  # 4: ⠄ 3
  'b',  # 5: ⠅ 13
  'i',  # 6: ⠆ 23
  'f',  # 7: ⠇ 123
  '/',  # 8: ⠈ 4
  'e',  # 9: ⠉ 14
  None,  # 10: ⠊ 24
  'd',  # 11: ⠋ 124
  ':',  # 12: ⠌ 34
  'h',  # 13: ⠍ 134
  'j',  # 14: ⠎ 234
  'g',  # 15: ⠏ 1234
  "'",  # 16: ⠐ 5
  'k',  # 17: ⠑ 15
  None,  # 18: ⠒ 25
  'm',  # 19: ⠓ 125
  ';',  # 20: ⠔ 35
  'l',  # 21: ⠕ 135
  's',  # 22: ⠖ 235
  'p',  # 23: ⠗ 1235
  None,  # 24: ⠘ 45
  'o',  # 25: ⠙ 145
  None,  # 26: ⠚ 245
  'n',  # 27: ⠛ 1245
  '!',  # 28: ⠜ 345
  'r',  # 29: ⠝ 1345
  't',  # 30: ⠞ 2345
  'q',  # 31: ⠟ 12345
  None,  # 32: ⠠ 6
  None,  # 33: ⠡ 16
  None,  # 34: ⠢ 26
  None,  # 35: ⠣ 126
  None,  # 36: ⠤ 36
  None,  # 37: ⠥ 136
  None,  # 38: ⠦ 236
  None,  # 39: ⠧ 1236
  None,  # 40: ⠨ 46
  None,  # 41: ⠩ 146
  None,  # 42: ⠪ 246
  None,  # 43: ⠫ 1246
  '.',  # 44: ⠬ 346
  None,  # 45: ⠭ 1346
  'w',  # 46: ⠮ 2346
  None,  # 47: ⠯ 12346
  '-',  # 48: ⠰ 56
  'u',  # 49: ⠱ 156
  None,  # 50: ⠲ 256
  'x',  # 51: ⠳ 1256
  None,  # 52: ⠴ 356
  'v',  # 53: ⠵ 1356
  None,  # 54: ⠶ 2356
  None,  # 55: ⠷ 12356
  None,  # 56: ⠸ 456
  'z',  # 57: ⠹ 1456
  None,  # 58: ⠺ 2456
  'y',  # 59: ⠻ 12456
  None,  # 60: ⠼ 3456
  None,  # 61: ⠽ 13456
  None,  # 62: ⠾ 23456
  None,  # 63: ⠿ 123456
]

if __name__ == '__main__':
  print('ALPHABET = [')
  braille_src = " a c,bif/e d:hjg'k m;lsp o n!rtq            . w -u x v   z y"


  def _braille_letter(i):
    if i == 0:
      return ' '
    elif i >= len(braille_src):
      return None
    elif braille_src[i] == ' ':
      return None
    return braille_src[i]


  def _bits(n):
    acc = []
    pos = 1
    while n:
      if n & 1:
        acc.append(str(pos))
      n >>= 1
      pos += 1
    return ''.join(acc) or '</>'


  for i in range(0, 2 ** 6):
    print('  %s,  # %s: %s %s' % (
      repr(_braille_letter(i)), i, chr(0x2800 + i), _bits(i)))

  print(']')
