import os

puzzles = [
  """
        ZBYYP      MKB
LBECR        KMRO      VSXO
DYYDR        RKSB      ROKN
        BKMO       PYYV
  """,
  """
    HQQV    DGTTA
    FQI  RQEMGV
  JQWUG YCVEJ RKEM

    RTKPV   DNWG
  """,
  """
           PWO
           AMB     WNN
EIAP  PMIL            TQNB
      PWB             NWZS
           EQZM  PIG
  """,
  """
OBNEQ  CHER GVZR  ZBGURE
OERQ              VPR
ORQ               ZNEX
XRL    FCHE FGBAR YBQR
  """,
  """
       MJOF
   EPPS   EJTI
PGG    FBS    TIPSF
  """,
  """
          FJH
      FXXM  URPQC
  FXUO         SNUUH
FJUT  BCJA  ORBQ  BRMN
  """,
  """
   EJCKT FTCIQP YJGGN
    URCEG NCPF   UJKR
DCEM RQKPV UVTGGV RKP
  """,
  """
GTC               MNY
     KTC HZU  BTWR
    YTBJW     HTWS
     YWTY YJF GTTP
RFNQ              RFS
  """,
]

_this_path = os.path.dirname(os.path.realpath(__file__))
_base_path = os.path.join(_this_path.split('/forge/')[0], 'forge')


def _read_lines(project_path):
  abs_path = os.path.join(_base_path, project_path)
  return open(abs_path).read().split('\n')


words = frozenset([
  word for word in _read_lines('data/words.txt')
])


def rotN(s, n):
  r = []
  for c in s:
    if c >= 'a' and c <= 'z':
      rotated = ((ord(c) + n) - ord('a')) % 26 + ord('a')
    elif c >= 'A' and c <= 'Z':
      rotated = ((ord(c) + n) - ord('A')) % 26 + ord('A')
    else:
      rotated = ord(c)
    r.append(chr(rotated))
  return ''.join(r)


for i, puzzle in enumerate(puzzles):
  print(puzzle)
  for n in range(1, 26):
    rotated = rotN(puzzle, n)
    rotated_words = rotated.split()
    if any([word.lower() in words for word in rotated_words]):
      print(rotated, 'rot%s' % n)
