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

var _ = Describe("Matches", func() {
	It("Initially does not match", func() {
		node := node.NewNode()
		Expect(node.Matches()).To(BeFalse())
	})

	It("Matches if constructed with a match weight", func() {
		node := node.NewNode(1.0)
		Expect(node.Matches()).To(BeTrue())
	})

	It("Matches after Match()", func() {
		node := node.NewNode(0)
		node.Match(1.0)
		Expect(node.Matches()).To(BeTrue())
	})
})

var _ = Describe("MaskPath", func() {
	It("Root inherits requirements from child", func() {
		root := node.NewNode()
		root.MaskPath("a")
		Expect(root.String()).To(Equal("Node('A', ' #', 0)"))
	})

	It("Rejects invalid input", func() {
		root := node.NewNode()
		err := root.MaskPath("🚫")
		Expect(err).To(HaveOccurred())
	})

	It("Root inherits complex requirements from child", func() {
		root := node.NewNode()
		root.MaskPath("abc")
		Expect(root.String()).To(Equal("Node('ABC', '   #', 0)"))
	})
})

var _ = Describe("MaskDistanceToChild", func() {
	It("Root inherits child at zero distance", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		child.ProvideMask, _ = mask.AlphabetMask('a')
		root.MaskDistanceToChild(0, child)
		Expect(root.String()).To(Equal("Node('a', '#', 1)"))
	})

	It("Root inherits simple requirements from child", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		child.ProvideMask, _ = mask.AlphabetMask('a')
		root.MaskDistanceToChild(5, child)
		Expect(root.String()).To(Equal("Node('a', '     #', 0)"))
	})

	It("Root ignores child requirements if root is a match", func() {
		root := node.NewNode(1.0)
		child := node.NewNode(1.0)
		child.ProvideMask, _ = mask.AlphabetMask('a')
		child.RequireMask = child.ProvideMask
		Expect(child.String()).To(Equal("Node('A', '#', 1)"))
		root.MaskDistanceToChild(5, child)
		Expect(root.String()).To(Equal("Node('a', '#    #', 1)"))
	})

	It("Root ignores child requirements if child is a match", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		child.ProvideMask, _ = mask.AlphabetMask('a')
		child.RequireMask = child.ProvideMask
		Expect(child.String()).To(Equal("Node('A', '#', 1)"))
		root.MaskDistanceToChild(5, child)
		Expect(root.String()).To(Equal("Node('a', '     #', 0)"))
	})

	It("Root inherits child requirements if child is not a match", func() {
		root := node.NewNode()
		child := node.NewNode()
		child.LengthsMask = 0b10
		child.ProvideMask, _ = mask.AlphabetMask('a')
		child.RequireMask = child.ProvideMask
		Expect(child.String()).To(Equal("Node('A', ' #', 0)"))
		root.MaskDistanceToChild(5, child)
		Expect(root.String()).To(Equal("Node('A', '      #', 0)"))
	})
})

var _ = Describe("MaskPathToChild", func() {
	It("Root inherits simple requirements from child", func() {
		root := node.NewNode()
		root.MaskPathToChild("a", node.NewNode(1.0))
		Expect(root.String()).To(Equal("Node('A', ' #', 0)"))
	})

	It("Rejects unsupported paths", func() {
		root := node.NewNode()
		err := root.MaskPathToChild("🚫", node.NewNode(1.0))
		Expect(err).To(HaveOccurred())
	})

	It("Root inherits complex requirements from child", func() {
		root := node.NewNode()
		root.MaskPathToChild("abc", node.NewNode(1.0))
		Expect(root.String()).To(Equal("Node('ABC', '   #', 0)"))
	})

	It("Root only requires path to child if the child is itself a match", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		bridge := node.NewNode(.5)
		bridge.MaskPathToChild("xyz", child)
		Expect(bridge.String()).To(Equal("Node('XYZ', '#  #', 0.5)"))
		root.MaskPathToChild("abc", bridge)
		Expect(root.String()).To(Equal("Node('ABCxyz', '   #  #', 0)"))
	})

	It("Root inherits all requirements from child if child is not a match", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		bridge := node.NewNode()
		bridge.MaskPathToChild("xyz", child)
		Expect(bridge.String()).To(Equal("Node('XYZ', '   #', 0)"))
		root.MaskPathToChild("abc", bridge)
		Expect(root.String()).To(Equal("Node('ABCXYZ', '      #', 0)"))
	})

	It("Root merges requirements from reference zero distance away", func() {
		reference := node.NewNode()
		reference.MaskPath("abc")
		root := node.NewNode()
		root.MaskPathToChild("", reference)
		Expect(root.String()).To(Equal("Node('ABC', '   #', 0)"))
	})
})

var _ = Describe("Union", func() {
	It("Empty nodes are a no-op", func() {
		source := node.NewNode()
		result := node.NewNode().Union(source)
		Expect(result.String()).To(Equal("Node('', '', 0)"))
	})

	It("Inherits from source", func() {
		source := node.NewNode()
		source.MaskPath("abc")
		result := node.NewNode().Union(source)
		Expect(result.String()).To(Equal("Node('ABC', '   #', 0)"))
	})

	It("Inherits max weight", func() {
		source := node.NewNode(1)
		result := node.NewNode(.5).Union(source)
		Expect(result.String()).To(Equal("Node('', '#', 1)"))
	})
})

var _ = Describe("Intersection", func() {
	It("Empty nodes are a no-op", func() {
		source := node.NewNode()
		result := node.NewNode().Intersection(source)
		Expect(result.String()).To(Equal("Node('', '', 0)"))
	})

	It("Intersects with source", func() {
		source := node.NewNode()
		source.MaskPath("abb")
		result := node.NewNode()
		result.MaskPath("aab")
		result.Intersection(source)
		Expect(result.String()).To(Equal("Node('AB', '   #', 0)"))
	})

	It("Detects impossible combinations", func() {
		source := node.NewNode()
		source.MaskPath("bcd")
		result := node.NewNode()
		result.MaskPath("abc")
		result.Intersection(source)
		Expect(result.String()).To(Equal("Node('ⒶBCⒹ', '', 0)"))
	})

	It("Inherits max (min) weight", func() {
		source := node.NewNode(.5)
		result := node.NewNode(1).Intersection(source)
		Expect(result.String()).To(Equal("Node('', '#', 0.5)"))
	})

	It("Blocks exits if other node has none", func() {
		source := node.NewNode(.5)
		result := node.NewNode(1)
		result.MaskPath("abc")
		Expect(result.String()).To(Equal("Node('ABC', '#  #', 1)"))
		result.Intersection(source)
		Expect(result.String()).To(Equal("Node('', '#', 0.5)"))
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
