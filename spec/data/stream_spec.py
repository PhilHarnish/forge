import mock

from spec.mamba import *

from data import stream


with description('stream'):
  with it('instantiates without errors'):
    expect(calling(stream.Stream)).not_to(raise_error)

  with it('subscribes without errors'):
    s = stream.Stream()
    expect(calling(s.subscribe, mock.Mock())).not_to(raise_error)

  with it('publishes to subscrbers'):
    s = stream.Stream()
    observer = mock.Mock()
    s.subscribe(observer)
    s.publish_value(1)
    expect(observer.on_next.call_args).to(equal(mock.call(1)))
