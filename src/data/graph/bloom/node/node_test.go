package node_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
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

func (iterator *TestIterator) Root() *node.Node {
	return nil
}

func (iterator *TestIterator) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return &TestItems{}
}

func (iterator *TestIterator) String() string {
	return "Test"
}

type TestItems struct{}

func (items *TestItems) HasNext() bool {
	return false
}

func (items *TestItems) Next() (string, node.NodeIterator) {
	return "", nil
}

func getFirstItem(i node.NodeIterator) (string, node.NodeIterator) {
	items := i.Items(node.NodeAcceptAll)
	return items.Next()
}

var _ = Describe("TestIterator", func() {
	It("Conforms with interface and compiles", func() {
		Expect(getFirstItem(&TestIterator{})).NotTo(BeNil())
	})
})
