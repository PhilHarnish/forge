import mock

from data import observable_meta
from spec.mamba import *

with description('observable_meta'):
  with it('instantiates'):
    expect(observable_meta.ObservableMeta()).to(be_empty)

  with it('publishes changes'):
    m = observable_meta.ObservableMeta()
    observer = mock.Mock()
    m.subscribe(observer)
    expect(observer.on_next.call_count).to(equal(0))
    m['something'] = 1
    expect(observer.on_next.call_count).to(equal(1))
    expect(observer.on_next.call_args).to(equal(mock.call(m)))
