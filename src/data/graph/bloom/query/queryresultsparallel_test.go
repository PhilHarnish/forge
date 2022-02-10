package query_test

import (
	"fmt"
	"math/rand"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
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
			name:    "example",
			results: newResults(0.5, "result"),
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
			name:    "a",
			results: newResults(1.0, "aa", 0.8, "ab"),
		}
		b := &testSource{
			name:    "b",
			results: newResults(0.5, "ba", 0.25, "bb"),
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

	It("Iterates streams returns results with decreasing value", func() {
		rand.Seed(GinkgoRandomSeed())
		size := 3
		a := &testSource{
			name:    "a",
			results: make([]query.QueryRow, size),
		}
		b := &testSource{
			name:    "b",
			results: make([]query.QueryRow, size),
		}
		c := &testSource{
			name:    "c",
			results: make([]query.QueryRow, size),
		}
		for size > 0 {
			size--
			score := rand.Float64()
			a.results[size] = newRow([]weight.WeightedString{
				{
					Weight: score,
					String: fmt.Sprintf("a%.02f", score),
				},
			})
			b.results[size] = newRow([]weight.WeightedString{
				{
					Weight: score,
					String: fmt.Sprintf("b%.02f", score),
				},
			})
			c.results[size] = newRow([]weight.WeightedString{
				{
					Weight: score,
					String: fmt.Sprintf("c%.02f", score),
				},
			})
		}
		a.SortResults()
		b.SortResults()
		c.SortResults()
		q := query.Select().From(a, b, c)
		Expect(q.String()).To(matchers.LookLike(""))
	})
})