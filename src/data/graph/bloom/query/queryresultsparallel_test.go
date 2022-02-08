package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
)

var _ = Describe("QueryResults parallel", func() {
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
				=======================
				0.25  | result | result
		`))
	})

	It("Reads multiple results from multiple sources", func() {
		a := &testSource{
			name: "a",
			results: []query.QueryResult{
				{
					Weight:  1.0,
					Strings: []string{"aa"},
				},
				{
					Weight:  .8,
					Strings: []string{"ab"},
				},
			},
		}
		b := &testSource{
			name: "b",
			results: []query.QueryResult{
				{
					Weight:  .5,
					Strings: []string{"ba"},
				},
				{
					Weight:  .25,
					Strings: []string{"bb"},
				},
			},
		}
		q := query.Select().From(a, b)
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM
					a,
					b;
				Score | a  | b
				===============
				0.50  | aa | ba
				---------------
				0.40  | ab | ba
				---------------
				0.25  | aa | bb
				---------------
				0.20  | ab | bb
		`))
	})
})
