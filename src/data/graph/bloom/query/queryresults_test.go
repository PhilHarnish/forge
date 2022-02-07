package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
)

var _ = Describe("QueryResults", func() {
	It("Reads from 1 source", func() {
		src := &testSource{name: "example"}
		q := query.Select().From(src)
		results := q.Results()
		Expect(results.HasNext()).To(BeTrue())
		Expect(results.Next().String()).To(Equal(""))
		Expect(src.exhausted).To(BeTrue())
	})
})
