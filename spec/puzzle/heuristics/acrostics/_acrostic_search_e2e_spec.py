from data import warehouse
from data.seek_sets import seek_set
from puzzle.heuristics.acrostics import _acrostic_search
from puzzle.puzzlepedia import prod_config
from spec.mamba import *


with description('acrostic e2e', 'end2end'):
  with before.each:
    warehouse.save()
    prod_config.init()

  with after.all:
    prod_config.reset()
    warehouse.restore()

  with it('finds saxophones'):
    seeking = seek_set.SeekSet(
        textwrap.dedent("""
          BigOldBell
          BootyJuker
          CorkChoker
          FacePinner
          FakeTurtle
          LemurPoker
          PixieProng
          SheepStick
          SqueezeToy
          TinyStools
        """.lower()).strip().split('\n'),
        sets_permutable=True,
        indexes=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    a = _acrostic_search.AcrosticSearch(seeking)
    expect(next(iter(a))).to(equal('saxophones'))
