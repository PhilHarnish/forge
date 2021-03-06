import mock

from data import observable_meta
from puzzle.puzzlepedia import solution_stream
from spec.mamba import *

with description('solution_stream'):
  with it('instantiates without errors'):
    expect(calling(
        solution_stream.SolutionStream,
        '1',
        observable_meta.ObservableMeta(),
    )).not_to(raise_error)

  with it('subscribes without errors'):
    s = solution_stream.SolutionStream('1', observable_meta.ObservableMeta())
    expect(calling(s.subscribe, mock.Mock())).not_to(raise_error)

  with context('when solutions change'):
    with before.each:
      self.solutions = observable_meta.ObservableMeta()
      self.stream = solution_stream.SolutionStream('1', self.solutions)

    with it('publishes to subscribers when solution changes'):
      observer = mock.Mock()
      self.stream.subscribe(observer)
      self.solutions['solution'] = 1337
      expect(observer.on_next.call_args).to(equal(mock.call(
          ('1', self.solutions))))

  with context('with nesting'):
    with before.each:
      self.children = [
        observable_meta.ObservableMeta(),
        observable_meta.ObservableMeta(),
      ]
      self.streams = [
        solution_stream.SolutionStream(str(i), meta) for i, meta in enumerate(
            self.children)
      ]
      self.parent_meta = observable_meta.ObservableMeta()
      self.parent = solution_stream.SolutionStream(
          'parent', self.parent_meta, self.streams)

    with it('publishes events from parent'):
      observer = mock.Mock()
      self.parent.subscribe(observer)
      self.parent_meta['solution'] = 1337
      expect(observer.on_next.call_args).to(equal(mock.call(
          ('parent', self.parent_meta))))

    with it('publishes events from children'):
      observer = mock.Mock()
      self.parent.subscribe(observer)
      self.children[0]['solution'] = 1337
      expect(observer.on_next.call_args).to(equal(mock.call(
          ('parent.0', self.children[0]))))
