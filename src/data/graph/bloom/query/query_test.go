package query_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
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
		∅
		`))
	})
})

type testSource struct {
	name    string
	results []query.QueryResult
}

func (source *testSource) Results() query.QueryResults {
	sourceCopy := &testSource{
		name:    source.name,
		results: make([]query.QueryResult, len(source.results)),
	}
	copy(sourceCopy.results, source.results)
	return sourceCopy
}

func (source *testSource) HasNext() bool {
	return len(source.results) > 0
}

func (source *testSource) Next() query.QueryResult {
	next := source.results[0]
	source.results = source.results[1:]
	return next
}

func (source *testSource) String() string {
	return source.name
}

var _ = Describe("From", func() {
	It("Adds 1 source", func() {
		src := &testSource{name: "example"}
		q := query.Select().From(src)
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM example;
				∅
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
				∅
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
				∅
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
				∅
		`))
	})
})
