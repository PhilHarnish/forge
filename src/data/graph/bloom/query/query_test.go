package query_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Select", func() {
	It("Instantiates a Query", func() {
		q := query.Select()
		Expect(q.String()).To(Equal(
			"SELECT *",
		))
	})

	It("Produces nil results by default", func() {
		Expect(query.Select().Next()).To(BeNil())
	})
})

var _ = Describe("Limits", func() {
	It("Sets a count limit", func() {
		q := query.Select().Limit(30)
		Expect(q.String()).To(Equal(
			"SELECT *\n" +
				"LIMIT 30",
		))
	})
})
