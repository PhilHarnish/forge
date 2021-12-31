from util.geometry import np2d


class Edge(object):
  _segment: np2d.Segment

  def __init__(self, segment: np2d.Segment) -> None:
    self._segment = segment
