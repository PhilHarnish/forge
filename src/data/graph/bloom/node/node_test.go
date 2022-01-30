package node_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("String", func() {
	It("Formats empty Nodes", func() {
		n := node.Node{}
		Expect(n.String()).To(Equal("Node('', '', 0)"))
	})

	It("Formats full Nodes", func() {
		n := node.Node{
			RequireMask: mask.ALL,
			ProvideMask: mask.ALL,
			LengthsMask: mask.Mask(0b1010101),
			MatchWeight: 1.0,
		}
		Expect(n.String()).To(Equal("Node('ABCDEFGHIJKLMNOPQRSTUVWXYZ -'', '# # # #', 1)"))
	})
})

type TestIterator struct{}

func (iterator *TestIterator) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return &TestItems{}
}

type TestItems struct{}

func (items *TestItems) Next() (string, *node.Node) {
	return "", nil
}

func testNodeAcceptor(path string, n *node.Node) weight.Weight {
	return 0
}

func getFirstItem(i node.NodeIterator) (string, *node.Node) {
	items := i.Items(testNodeAcceptor)
	return items.Next()
}

var _ = Describe("TestIterator", func() {
	It("Conforms with interface and compiles", func() {
		Expect(getFirstItem(&TestIterator{})).NotTo(BeNil())
	})
})
