package node_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Match", func() {
	It("Initially does not match", func() {
		node := node.NewNode()
		Expect(node.String()).To(Equal("Node('', '', 0)"))
	})

	It("Match indicated in String output", func() {
		node := node.NewNode()
		node.Match(0.5)
		Expect(node.String()).To(Equal("Node('', '#', 0.5)"))
	})

	It("Rejects duplicate attempts", func() {
		node := node.NewNode()
		node.Match(0.5)
		Expect(func() {
			node.Match(0.5)
		}).To(Panic())
	})
})

var _ = Describe("String", func() {
	It("Formats empty Nodes", func() {
		n := node.NewNode()
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
	return &node.Node{}
}

func (iterator *TestIterator) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return &TestItems{"a", "b"}
}

func (iterator *TestIterator) String() string {
	return node.Format("TestIterator", iterator.Root())
}

type TestItems []string

func (items *TestItems) HasNext() bool {
	return len(*items) > 0
}

func (items *TestItems) Next() (string, node.NodeIterator) {
	if !items.HasNext() {
		return "", nil
	}
	item := (*items)[0]
	*items = (*items)[1:]
	return item, &TestIterator{}
}

func getFirstItem(i node.NodeIterator) (string, node.NodeIterator) {
	items := i.Items(node.NodeAcceptAll)
	return items.Next()
}

var _ = Describe("TestIterator", func() {
	var iterator *TestIterator

	BeforeEach(func() {
		iterator = &TestIterator{}
	})

	It("Conforms with interface and compiles", func() {
		_, value := getFirstItem(iterator)
		Expect(value).NotTo(BeNil())
	})

	It("Produces string results", func() {
		Expect(iterator.String()).To(Equal("TestIterator('', '', 0)"))
	})

	It("Produces shallow string results", func() {
		Expect(node.StringChildren(iterator)).To(matchers.LookLike(`
				TestIterator('', '', 0)
				├─a = TestIterator('', '', 0)
				└─b = TestIterator('', '', 0)
		`))
	})

	It("Produces deeper string results", func() {
		Expect(node.StringChildren(iterator, 2)).To(matchers.LookLike(`
				TestIterator('', '', 0)
				├─a = TestIterator('', '', 0)
				│ ├─a = TestIterator('', '', 0)
				│ └─b = TestIterator('', '', 0)
				└─b = TestIterator('', '', 0)
				• ├─a = TestIterator('', '', 0)
				• └─b = TestIterator('', '', 0)
		`))
	})
})
