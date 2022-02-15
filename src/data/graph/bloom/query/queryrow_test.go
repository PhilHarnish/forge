package query_test

import (
	"container/heap"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

var _ = Describe("QueryRowHeader", func() {
	It("is initially empty", func() {
		q := query.Select()
		Expect(q.Header().Labels()).To(Equal([]string{}))
	})

	It("discovers column headers from query sources", func() {
		q := query.Select().From(emptySource).As("example")
		Expect(q.Header().Labels()).To(Equal([]string{"example"}))
	})

	It("labels child sources automatically", func() {
		child := query.Select().From(emptySource).From(emptySource)
		parent := query.Select().From(emptySource).From(child)
		Expect(parent.Header().Labels()).To(Equal([]string{"_0", "_1._0", "_1._1"}))
	})

	It("labels child sources with names", func() {
		child := query.Select().From(emptySource).As("left").From(emptySource).As("right")
		parent := query.Select().From(emptySource).As("parent").From(child).As("child")
		Expect(parent.Header().Labels()).To(Equal([]string{"parent", "child.left", "child.right"}))
	})
})

var _ = Describe("QueryRow", func() {
	It("initially has 1.0 weight", func() {
		q := query.Select()
		row := query.NewQueryRowForQuery(q)
		Expect(row.Weight()).To(Equal(1.0))
	})

	It("expects the number of inputs to match the number of sources", func() {
		q := query.Select().From(emptySource)
		row := query.NewQueryRowForQuery(q)
		Expect(func() { row.AssignCells(0, row.Weight(), nil) }).To(Panic())
	})

	It("expects the number of inputs to match the number of sources", func() {
		q := query.Select().From(emptySource)
		row := query.NewQueryRowForQuery(q)
		row.AssignCells(
			0,
			row.Weight(),
			[]query.QueryRowCell{weight.WeightedString{Weight: .50, String: "example"}})
		Expect(row.Weight()).To(Equal(.50))
		Expect(row.Cells()).To(HaveLen(1))
		Expect(row.Cells()[0].String).To(Equal("example"))
	})

	It("understands composed queries require differently sized assignments", func() {
		child := query.Select().From(emptySource).As("a").From(emptySource).As("b")
		parent := query.Select().From(emptySource).As("left").From(child).As("right")
		row := query.NewQueryRowForQuery(parent)
		cells := []query.QueryRowCell{weight.WeightedString{Weight: .50, String: "left"}}
		row.AssignCells(0, row.Weight(), cells)
		cells = append(cells, weight.WeightedString{Weight: .50, String: "right"})
		row.AssignCells(1, row.Weight(), cells)
		Expect(row.Weight()).To(Equal(.5 * .5 * .5))
		Expect(row.Cells()).To(HaveLen(3))
		Expect(row.Cells()[0].String).To(Equal("left"))
		Expect(row.Cells()[1].String).To(Equal("left"))
		Expect(row.Cells()[2].String).To(Equal("right"))
	})
})

var _ = Describe("QueryRows", func() {
	It("implements the heap interface", func() {
		h := query.QueryRows{}
		heap.Init(&h)
	})

	It("offers rows in decreasing weight", func() {
		var h query.QueryRows = newResults(1.0, "first", 0.1, "last", 0.5, "middle")
		heap.Init(&h)
		row := h.Next()
		Expect(row.Weight()).To(Equal(1.0))
		Expect(row.Cells()[0].String).To(Equal("first"))
		row = h.Next()
		Expect(row.Weight()).To(Equal(0.5))
		Expect(row.Cells()[0].String).To(Equal("middle"))
		row = h.Next()
		Expect(row.Weight()).To(Equal(0.1))
		Expect(row.Cells()[0].String).To(Equal("last"))
	})
})
