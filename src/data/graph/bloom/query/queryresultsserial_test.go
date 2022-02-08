package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
)

var _ = Describe("QueryResults", func() {
	It("Reads from 1 source", func() {
		src := &testSource{
			name: "example",
			results: []query.QueryResult{
				{
					Weight:  0.0,
					Strings: []string{"result"},
				},
			},
		}
		q := query.Select().From(src)
		Expect(q.String()).To(matchers.LookLike(`
		SELECT *
		FROM example;
		Score | example
		===============
		0.00  | result
		`))
	})
})
