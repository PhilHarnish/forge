from data.graph.multi import multi_state
from spec.mamba import *

with description('multi_state'):
  with it('instantiates empty'):
    expect(calling(multi_state.State)).not_to(raise_error)

  with it('compares empty objects as equal'):
    expect(multi_state.State()).to(equal(multi_state.State()))

  with description('combination'):
    with it('combining BLANKs yields BLANK'):
      expect(multi_state.BLANK & multi_state.BLANK).to(be(multi_state.BLANK))

    with it('combining other with BLANK yields other'):
      for given in [multi_state.State({'a': 1}), multi_state.State({'b': 2})]:
        expect(calling(given.__and__, multi_state.BLANK)).to(equal(given))

    with it('combining BLANK with other yields other'):
      for given in [multi_state.State({'a': 1}), multi_state.State({'b': 2})]:
        expect(calling(multi_state.BLANK.__and__, given)).to(equal(given))

    with it('combining two non-overlapping states gives union'):
      a = multi_state.State({'a': 1})
      b = multi_state.State({'b': 2})
      expect(a & b).to(equal(multi_state.State({'a': 1, 'b': 2})))

    with it('combining two incompatible overlapping states gives None'):
      a = multi_state.State({'a': 1, 'c': 3})
      b = multi_state.State({'a': 2, 'c': 3})
      expect(a & b).to(equal(None))

    with it('combining two compatible overlapping states gives union'):
      a = multi_state.State({'a': 1, 'c': 3})
      b = multi_state.State({'b': 2, 'c': 3})
      expect(a & b).to(equal(multi_state.State({'a': 1, 'b': 2, 'c': 3})))
