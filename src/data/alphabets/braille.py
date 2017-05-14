ALPHABET = [
  ' ',  # 0: ⠀ </>
  'a',  # 1: ⠁ 1
  ',',  # 2: ⠂ 2
  'b',  # 3: ⠃ 12
  "'",  # 4: ⠄ 3
  'k',  # 5: ⠅ 13
  ';',  # 6: ⠆ 23
  'l',  # 7: ⠇ 123
  '^',  # 8: ⠈ 4
  'c',  # 9: ⠉ 14
  'i',  # 10: ⠊ 24
  'f',  # 11: ⠋ 124
  '/',  # 12: ⠌ 34  (technically, ⠸⠌	456 34)
  'm',  # 13: ⠍ 134
  's',  # 14: ⠎ 234
  'p',  # 15: ⠏ 1234
  None,  # 16: ⠐ 5  (technically, indicates start of ( or ))
  'e',  # 17: ⠑ 15
  ':',  # 18: ⠒ 25
  'h',  # 19: ⠓ 125
  '*',  # 20: ⠔ 35  (nonstandard)
  'o',  # 21: ⠕ 135
  '!',  # 22: ⠖ 235
  'r',  # 23: ⠗ 1235
  None,  # 24: ⠘ 45
  'd',  # 25: ⠙ 145
  'j',  # 26: ⠚ 245
  'g',  # 27: ⠛ 1245
  None,  # 28: ⠜ 345
  'n',  # 29: ⠝ 1345
  't',  # 30: ⠞ 2345
  'q',  # 31: ⠟ 12345
  '|',  # 32: ⠠ 6  (nonstandard)
  '\\',  # 33: ⠡ 16  (technically, ⠸⠡	456 16)
  '?',  # 34: ⠢ 26  (nonstandard)
  None,  # 35: ⠣ 126
  '-',  # 36: ⠤ 36
  'u',  # 37: ⠥ 136
  '?',  # 38: ⠦ 236
  'v',  # 39: ⠧ 1236
  None,  # 40: ⠨ 46
  None,  # 41: ⠩ 146
  None,  # 42: ⠪ 246
  None,  # 43: ⠫ 1246
  None,  # 44: ⠬ 346
  'x',  # 45: ⠭ 1346
  None,  # 46: ⠮ 2346
  None,  # 47: ⠯ 12346
  None,  # 48: ⠰ 56
  None,  # 49: ⠱ 156
  '.',  # 50: ⠲ 256
  None,  # 51: ⠳ 1256
  ')',  # 52: ⠴ 356  (technically, a closing mark)
  'z',  # 53: ⠵ 1356
  '"',  # 54: ⠶ 2356  (technically, ⠄⠶	3 2356)
  None,  # 55: ⠷ 12356
  None,  # 56: ⠸ 456
  None,  # 57: ⠹ 1456
  'w',  # 58: ⠺ 2456
  None,  # 59: ⠻ 12456
  '#',  # 60: ⠼ 3456
  'y',  # 61: ⠽ 13456
  None,  # 62: ⠾ 23456
  None,  # 63: ⠿ 123456
]

# TODO: Convert numbers.


if __name__ == '__main__':
  braille_src = (
    ' a,b\'k;l^cif/msp e:h*o!r djg ntq| ? -u?v     x    . )z\"   w #y')

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


  print('ALPHABET = [')
  for i in range(0, 2 ** 6):
    print('  %s,  # %s: %s %s' % (
      repr(_braille_letter(i)), i, chr(0x2800 + i), _bits(i)))
  print(']')
