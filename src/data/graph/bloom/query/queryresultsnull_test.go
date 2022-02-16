package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
)

var _ = Describe("queryResultsNull", func() {
	It("Has no results", func() {
		q := query.Select()
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *;
				∅
		`))
	})
})
