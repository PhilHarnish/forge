package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

var _ = Describe("QueryResults", func() {
	It("Reads from 1 source", func() {
		src := &testSource{
			name: "example",
			results: []weight.WeightedString{
				{
					Weight: 0.0,
					String: "result",
				},
			},
		}
		q := query.Select().From(src)
		results := q.Results()
		Expect(results.HasNext()).To(BeTrue())
		Expect(results.Next().String).To(Equal("result"))
		Expect(results.HasNext()).To(BeFalse())
	})
})
