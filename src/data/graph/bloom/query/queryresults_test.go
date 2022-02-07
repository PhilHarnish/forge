package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

var emptySource = &testSource{
	name:    "example",
	results: []weight.WeightedString{},
}

var _ = Describe("QueryResults", func() {
	It("Can read from zero source", func() {
		q := query.Select().From(emptySource)
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM example;
				∅
		`))
	})

	It("Can read from 1 source", func() {
		q := query.Select().From(emptySource)
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM example;
				∅
		`))
	})

	It("Can read from 2+ sources", func() {
		q := query.Select().From(emptySource).From(emptySource)
		Expect(q.String()).To(matchers.LookLike(`
			SELECT *
			FROM
				example,
				example;
			∅
		`))
	})
})
