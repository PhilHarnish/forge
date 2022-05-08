package op_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
)

var _ = Describe("Items", func() {
	It("Initially has no items", func() {
		operation := op.And()
		items := node.NodeGenerateAll.Items(operation)
		Expect(items.HasNext()).To(BeFalse())
	})
})
