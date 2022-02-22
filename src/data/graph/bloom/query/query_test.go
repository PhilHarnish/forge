package query_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Select", func() {
	It("Instantiates a Query", func() {
		q := query.Select()
		Expect(q.String()).To(matchers.LookLike(`
		SELECT *;
		`))
	})
})

func newResults(results ...interface{}) []query.QueryRow {
	result := []query.QueryRow{}
	x := 0
	for x < len(results) {
		result = append(result, query.NewQueryRow([]weight.WeightedString{
			{
				Weight: results[x].(weight.Weight),
				String: results[x+1].(string),
			},
		}))
		x += 2
	}
	return result
}

type testSource struct {
	name    string
	results query.QueryRows
}

func (source *testSource) Header() query.QueryRowHeader {
	return source
}

func (source *testSource) Results() query.QueryResults {
	rows := make([]query.QueryRow, len(source.results))
	copy(rows, source.results)
	return query.NewQueryResults(source.Header(), rows)
}

func (source *testSource) Labels() []string {
	return []string{"Text"}
}

func (source *testSource) String(includeResults ...bool) string {
	return source.name
}

var _ = Describe("testSource", func() {
	It("implements the QueryResultsSource interface", func() {
		var src query.QueryResultsSource = &testSource{name: "example"}
		Expect(src).NotTo(Equal(nil))
	})

	It("implements the QueryResultsSource interface, recursively", func() {
		var src query.QueryResultsSource = query.Select().From(&testSource{name: "example"})
		Expect(src).NotTo(Equal(nil))
	})
})

var _ = Describe("From", func() {
	It("Adds 1 source", func() {
		src := &testSource{name: "example"}
		q := query.Select().From(src)
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM example;
		`))
	})

	It("Adds multiple sources", func() {
		q := query.Select().From(
			&testSource{name: "example1"},
			&testSource{name: "example2"},
		)
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM
					example1,
					example2;
		`))
	})

	It("Adds multiple named sources", func() {
		q := query.Select().From(
			&testSource{name: "example1"},
		).As("A").From(
			&testSource{name: "example2"},
		).As("B")
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM
					example1 AS A,
					example2 AS B;
		`))
	})

	It("Rejects naming zero sources", func() {
		q := query.Select()
		Expect(func() {
			q.As("A")
		}).Should(Panic())
	})

	It("Rejects duplicate names", func() {
		q := query.Select().From(
			&testSource{name: "example1"},
		).As("A")
		Expect(func() {
			q.As("B")
		}).Should(Panic())
	})
})

var _ = Describe("Limits", func() {
	It("Sets a count limit", func() {
		q := query.Select().Limit(30)
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				LIMIT 30;
		`))
	})
})

var _ = Describe("Functional tests", func() {
	It("finds intersecting regular expressions", func() {
		a := retrie.NewReTrie("a*b*c*", 1.0)
		b := retrie.NewReTrie("abc|xyz", 1.0)
		q := query.Select().From(op.And(a, b))
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM (((ReTrie: 100 abc ●●●···) && (ReTrie: abcxyz ◌◌◌●)): abc ◌◌◌●);
				Score | Text
				============
				1.00  | abc
		`))
	})

	FIt("finds words matching regular expressions", func() {
		a := retrie.NewReTrie("a+.*b+.*c+.*", 1.0)
		b := trie.NewTrie()
		b.Add("banana", 1.0)
		b.Link("a", trie.NewTrie())
		child := b.Get("a")
		child.Add("pple", 1.0)
		child.Add("rabic", 1.0)
		child.Add("bstract", 1.0)
		merged := op.And(a, b)
		Expect(node.StringChildren(merged, 3)).To(matchers.LookLike(`
		`))
		q := query.Select().From(op.And(a, b))
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM (((ReTrie: 100 abc ●●●···) && (ReTrie: abcxyz ◌◌◌●)): abc ◌◌◌●);
				Score | Text
				============
				1.00  | abc
		`))
	})
})
