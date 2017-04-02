import collections

from expects import *
from src.data import meta

with description('Meta'):
  with it('instantiates'):
    expect(meta.Meta()).to(be_empty)

  with it('retrieves items like a dict would'):
    m = meta.Meta(key=1)
    expect(m).to(have_key('key'))
    expect(m['key']).to(equal(1))

  with it('has extra accessors for getting "first" item'):
    m = meta.Meta(key=1)
    expect(m.first()).to(equal(('key', 1)))

  with it('has extra accessors for peeking first value'):
    m = meta.Meta(key=1)
    expect(m.peek()).to(equal('key'))

  with it('orders items by weight'):
    m = meta.Meta()
    m['a'] = .25
    m['b'] = .75
    expect(m.peek()).to(equal('b'))
