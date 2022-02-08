package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
)

var _ = Describe("QueryResults", func() {
	It("Reads from 2+ empty source", func() {
		src := &testSource{
			name: "example",
		}
		q := query.Select().From(src).As("a").From(src).As("b")
		Expect(q.String()).To(matchers.LookLike(`
		SELECT *
		FROM
			example AS a,
			example AS b;
		∅
		`))
	})

	It("Reads from 2+ populated sources", func() {
		src := &testSource{
			name: "example",
			results: []query.QueryResult{
				{
					Weight:  0.5,
					Strings: []string{"result"},
				},
			},
		}
		q := query.Select().From(src).As("a").From(src).As("b")
		Expect(q.String()).To(matchers.LookLike(`
			SELECT *
			FROM
				example AS a,
				example AS b;
			Score | a      | b
			-----------------------
			0.25  | result | result
		`))
	})
})
