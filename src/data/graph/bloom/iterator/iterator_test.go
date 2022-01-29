package iterator_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/iterator"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

type TestIterator struct{}

func (iterator *TestIterator) Items() iterator.IteratorItems {
	return &TestIteratorItems{}
}

type TestIteratorItems struct{}

func (items *TestIteratorItems) Next() *iterator.IteratorItem {
	return &iterator.IteratorItem{}
}

func getFirstItem(i iterator.Iterator) *iterator.IteratorItem {
	items := i.Items()
	return items.Next()
}

var _ = Describe("TestIterator", func() {
	It("Conforms with interface and compiles", func() {
		Expect(getFirstItem(&TestIterator{})).NotTo(BeNil())
	})
})
