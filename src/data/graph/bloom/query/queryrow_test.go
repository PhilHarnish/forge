package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
)

var _ = Describe("QueryRow", func() {
	It("initially has zero weight", func() {
		q := query.Select()
		queryRow := query.NewQueryRowFromCells(q, nil)
		Expect(queryRow.Weight()).To(Equal(0.0))
	})

	It("expects the number of inputs to match the number of sources", func() {
		q := query.Select().From(emptySource)
		Expect(func() { query.NewQueryRowFromCells(q, nil) }).To(Panic())
	})
})
