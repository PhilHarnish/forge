package query_test

import (
	"fmt"
	"math"
	"math/rand"
	"sort"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
)

var _ = Describe("QueryResults parallel", func() {
	It("reads from 2+ empty source", func() {
		src := &testSource{
			name: "example",
		}
		q := query.Select().From(src).As("a").From(src).As("b")
		Expect(q.String(true)).To(matchers.LookLike(`
		SELECT *
		FROM
			example AS a,
			example AS b;
		∅
		`))
	})

	It("reads from 2+ populated sources", func() {
		src := &testSource{
			name:    "example",
			results: newResults(0.5, "result"),
		}
		q := query.Select().From(src).As("a").From(src).As("b")
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM
					example AS a,
					example AS b;
				Score | a      | b
				=======================
				0.25  | result | result
		`))
	})

	It("reads multiple results from multiple sources", func() {
		a := &testSource{
			name:    "a",
			results: newResults(1.0, "aa", 0.8, "ab"),
		}
		b := &testSource{
			name:    "b",
			results: newResults(0.5, "ba", 0.25, "bb"),
		}
		q := query.Select().From(a).As("a").From(b).As("b")
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM
					a AS a,
					b AS b;
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

	It("reads up until a given limit", func() {
		a := &testSource{
			name:    "a",
			results: newResults(1.0, "aa", 0.8, "ab"),
		}
		q := query.Select().From(a, a, a).Limit(4)
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM
					a,
					a,
					a
				LIMIT 4;
				Score | Text | Text | Text
				==========================
				1.00  | aa   | aa   | aa
				--------------------------
				0.80  | ab   | aa   | aa
				--------------------------
				0.80  | aa   | aa   | ab
				--------------------------
				0.80  | aa   | ab   | aa
		`))
	})

	It("iterates streams returns results with decreasing value", func() {
		rand.Seed(GinkgoRandomSeed())
		size := 5
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
		i := 0
		score := rand.Float64()
		for i < size {
			a.results[i] = query.NewQueryRow([]query.QueryRowCell{
				{
					Weight: score,
					String: fmt.Sprintf("a%.02f", score),
				},
			})
			score = rand.Float64()
			b.results[i] = query.NewQueryRow([]query.QueryRowCell{
				{
					Weight: score,
					String: fmt.Sprintf("b%.02f", score),
				},
			})
			score = rand.Float64()
			c.results[i] = query.NewQueryRow([]query.QueryRowCell{
				{
					Weight: score,
					String: fmt.Sprintf("c%.02f", score),
				},
			})
			i++
		}
		sort.Sort(a.results)
		sort.Sort(b.results)
		sort.Sort(c.results)
		q := query.Select().From(a, b, c)
		results := q.Results()
		lastWeight := math.Inf(1)
		count := 0
		for results.HasNext() {
			next := results.Next()
			nextWeight := next.Weight()
			delta := math.Abs(lastWeight - nextWeight)
			// Implement fuzzy <= by ensuring the drop mostly negative, with up to 1e-8 error.
			fuzzyLessThan := (nextWeight < lastWeight) || delta < 1e-8
			Expect(fuzzyLessThan).To(BeTrue())
			lastWeight = next.Weight()
			count++
		}
		Expect(count).To(Equal(len(a.results) * len(b.results) * len(c.results)))
	})
})
