from data.logic import _neighbor_predicates, _reference
from spec.mamba import *

with description('_neighbor_predicates'):
  with before.each:
    self.model = mock.Mock(
        get_variables=lambda constraints: 'name["%s"]' % constraints['name'],
    )

    self.a = _reference.Reference(self.model, {'name': 'a'})
    self.b = _reference.Reference(self.model, {'name': 'b'})
    self.c = _reference.Reference(self.model, {'name': 'c'})

  with _description('from_edges'):
    with it('handles empty list'):
      expect(calling(
          _neighbor_predicates.from_edges, [], False, self.a)
      ).not_to(raise_error)

    with it('handles small list'):
      expect(calling(
          _neighbor_predicates.from_edges, [(self.a, self.b)], False, self.b,
      )).not_to(raise_error)

    with it('handles small, directed list'):
      expect(calling(
          _neighbor_predicates.from_edges, [(self.a, self.b)], True, self.b,
      )).not_to(raise_error)

    with it('handles cycle'):
      expect(calling(
          _neighbor_predicates.from_edges, [
            (self.a, self.b),
            (self.b, self.c),
            (self.c, self.a),
          ], False, self.a)
      ).not_to(raise_error)

    with it('creates a graph'):
      predicates = _neighbor_predicates.from_edges([
        (self.a, self.b),
        (self.b, self.c),
        (self.c, self.a),
      ], False, self.a)
      expect(predicates).to(be_a(_neighbor_predicates._NeighborPredicates))
      expect(predicates._graph).to(be_a(_neighbor_predicates._Graph))
      expect(predicates._graph).to(have_len(3))
      expect(predicates._graph).to(equal({
        self.a: {self.b, self.c},
        self.b: {self.a, self.c},
        self.c: {self.a, self.b},
      }))
