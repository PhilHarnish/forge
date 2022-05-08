package node_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("Copy", func() {
	It("copies do not modify original", func() {
		original := node.NewNode()
		nodeCopy := original.Copy()
		original.MatchWeight = 1.0
		Expect(nodeCopy.MatchWeight).To(Equal(0.0))
	})
})

var _ = Describe("Match", func() {
	It("Initially does not match", func() {
		node := node.NewNode()
		Expect(node.String()).To(Equal("Node"))
	})

	It("Match indicated in String output", func() {
		node := node.NewNode()
		node.Match(0.5)
		Expect(node.String()).To(Equal("Node: 50 ●"))
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

func concatLengths(a mask.Mask, b mask.Mask) *node.Node {
	aNode := node.NewNode()
	aNode.LengthsMask = a
	bNode := node.NewNode()
	bNode.LengthsMask = b
	aNode.MaskPrependChild(bNode)
	return aNode
}

var _ = Describe("MaskConcatenateChild", func() {
	It("Returns zeros out for zeros in", func() {
		Expect(concatLengths(0b0, 0b0).String()).To(Equal("Node"))
	})

	It("Returns one for ones in", func() {
		Expect(concatLengths(0b1, 0b1).String()).To(Equal("Node: 0 ●"))
	})

	It("Returns shifted input for twos", func() {
		Expect(concatLengths(0b10, 0b10).String()).To(Equal("Node: ◌◌●"))
	})

	It("Mirrors input for multiples", func() {
		first := mask.Mask((1 << 3) | (1 << 5))
		second := mask.Mask((1 << 7) | (1 << 11))
		expected := mask.Mask(
			(1<<3)*(1<<7) |
				(1<<3)*(1<<11) |
				(1<<5)*(1<<7) |
				(1<<5)*(1<<11))
		Expect(concatLengths(first, second).String()).To(Equal(
			"Node: " + mask.LengthString(expected)))
	})

	It("Handles (a, repeats)", func() {
		a := mask.Mask(0b10100000000)
		repeats := mask.RepeatLengths(0b100, 4)
		Expect(concatLengths(a, repeats).String()).To(Equal(
			"Node: ◌◌◌◌◌◌◌◌◌◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●●···"))
	})

	It("Handles (repeats, b)", func() {
		repeats := mask.RepeatLengths(0b100, 4)
		b := mask.Mask(0b10100000000)
		Expect(concatLengths(repeats, b).String()).To(Equal(
			"Node: ◌◌◌◌◌◌◌◌◌◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●●···"))
	})
})

var _ = Describe("MaskEdgeMask", func() {
	It("Applies simple mask", func() {
		root := node.NewNode()
		edgeMask, _ := mask.AlphabetMaskRange('a', 'a')
		root.MaskEdgeMask(edgeMask)
		Expect(root.String()).To(Equal("Node: A"))
	})

	It("Applies compound mask", func() {
		root := node.NewNode()
		edgeMask, _ := mask.AlphabetMaskRange('a', 'c')
		root.MaskEdgeMask(edgeMask)
		Expect(root.String()).To(Equal("Node: ABC"))
	})
})

var _ = Describe("MaskEdgeMaskToChild", func() {
	It("Applies simple mask, assumes one option is requied", func() {
		root := node.NewNode()
		edgeMask, _ := mask.AlphabetMaskRange('a', 'a')
		root.MaskEdgeMaskToChild(edgeMask, node.NewNode(1.0))
		Expect(root.String()).To(Equal("Node: A ◌●"))
	})

	It("Applies compound mask, assumes multiple paths are not required", func() {
		root := node.NewNode()
		edgeMask, _ := mask.AlphabetMaskRange('a', 'c')
		root.MaskEdgeMaskToChild(edgeMask, node.NewNode(1.0))
		Expect(root.String()).To(Equal("Node: abc ◌●"))
	})

	It("Clears requirements when new paths are added", func() {
		root := node.NewNode()
		edgeMask, _ := mask.AlphabetMaskRange('a', 'c')
		bRequired := node.NewNode()
		bRequired.MaskPath("b")
		root.MaskEdgeMaskToChild(edgeMask, node.NewNode(1.0))
		root.Union(bRequired)
		Expect(root.String()).To(Equal("Node: abc ◌●"))
		Expect(root.RequireMask).To(Equal(mask.Mask(0)))
	})
})

var _ = Describe("MaskPath", func() {
	It("Root inherits requirements from child", func() {
		root := node.NewNode()
		root.MaskPath("a")
		Expect(root.String()).To(Equal("Node: A ◌●"))
	})

	It("Rejects invalid input", func() {
		root := node.NewNode()
		err := root.MaskPath("🚫")
		Expect(err).To(HaveOccurred())
	})

	It("Root inherits complex requirements from child", func() {
		root := node.NewNode()
		root.MaskPath("abc")
		Expect(root.String()).To(Equal("Node: ABC ◌◌◌●"))
	})
})

var _ = Describe("MaskDistanceToChild", func() {
	It("Root inherits child at zero distance", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		child.ProvideMask, _ = mask.AlphabetMask('a')
		root.MaskDistanceToChild(0, child)
		Expect(root.String()).To(Equal("Node: 100 a ●"))
	})

	It("Root inherits simple requirements from child", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		child.ProvideMask, _ = mask.AlphabetMask('a')
		root.MaskDistanceToChild(5, child)
		Expect(root.String()).To(Equal("Node: a ◌◌◌◌◌●"))
	})

	It("Root observes child requirements regardless of root match", func() {
		root := node.NewNode(1.0)
		child := node.NewNode()
		child.ProvideMask, _ = mask.AlphabetMask('a')
		child.RequireMask = child.ProvideMask
		Expect(child.String()).To(Equal("Node: A"))
		root.MaskDistanceToChild(5, child)
		Expect(root.String()).To(Equal("Node: 100 A ●"))
	})

	It("Root ignores child requirements if child is a match", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		child.ProvideMask, _ = mask.AlphabetMask('a')
		child.RequireMask = child.ProvideMask
		Expect(child.String()).To(Equal("Node: 100 A ●"))
		root.MaskDistanceToChild(5, child)
		Expect(root.String()).To(Equal("Node: a ◌◌◌◌◌●"))
	})

	It("Root inherits child requirements if child is not a match", func() {
		root := node.NewNode()
		child := node.NewNode()
		child.LengthsMask = 0b10
		child.ProvideMask, _ = mask.AlphabetMask('a')
		child.RequireMask = child.ProvideMask
		Expect(child.String()).To(Equal("Node: A ◌●"))
		root.MaskDistanceToChild(5, child)
		Expect(root.String()).To(Equal("Node: A ◌◌◌◌◌◌●"))
	})
})

var _ = Describe("MaskPathToChild", func() {
	It("Root inherits simple requirements from child", func() {
		root := node.NewNode()
		root.MaskPathToChild("a", node.NewNode(1.0))
		Expect(root.String()).To(Equal("Node: A ◌●"))
	})

	It("Rejects unsupported paths", func() {
		root := node.NewNode()
		err := root.MaskPathToChild("🚫", node.NewNode(1.0))
		Expect(err).To(HaveOccurred())
	})

	It("Root inherits complex requirements from child", func() {
		root := node.NewNode()
		root.MaskPathToChild("abc", node.NewNode(1.0))
		Expect(root.String()).To(Equal("Node: ABC ◌◌◌●"))
	})

	It("Root only requires path to child if the child is itself a match", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		bridge := node.NewNode(.5)
		bridge.MaskPathToChild("xyz", child)
		Expect(bridge.String()).To(Equal("Node: 50 XYZ ●◌◌●"))
		root.MaskPathToChild("abc", bridge)
		Expect(root.String()).To(Equal("Node: ABCxyz ◌◌◌●◌◌●"))
	})

	It("Root inherits all requirements from child if child is not a match", func() {
		root := node.NewNode()
		child := node.NewNode(1.0)
		bridge := node.NewNode()
		bridge.MaskPathToChild("xyz", child)
		Expect(bridge.String()).To(Equal("Node: XYZ ◌◌◌●"))
		root.MaskPathToChild("abc", bridge)
		Expect(root.String()).To(Equal("Node: ABCXYZ ◌◌◌◌◌◌●"))
	})

	It("Root merges requirements from reference zero distance away", func() {
		reference := node.NewNode()
		reference.MaskPath("abc")
		root := node.NewNode()
		root.MaskPathToChild("", reference)
		Expect(root.String()).To(Equal("Node: ABC ◌◌◌●"))
	})
})

var _ = Describe("MaskPrependChild", func() {
	It("Prepends child (which matches)", func() {
		child := node.NewNode(1.0)
		parent := node.NewNode()
		parent.MaskPathToChild("abc", child)
		root := node.NewNode(1.0) // NB: Root DOES match.
		root.MaskPathToChild("xy", node.NewNode(1.0))
		root.MaskPrependChild(parent)
		// Result: a->b->c (match) ->x->y (optional).
		Expect(root.String()).To(Equal("Node: ABCxy ◌◌◌●◌●"))
	})

	It("Prepends child (which does not match)", func() {
		child := node.NewNode(1.0)
		parent := node.NewNode()
		parent.MaskPathToChild("abc", child)
		root := node.NewNode() // NB: Root DOES NOT match.
		root.MaskPathToChild("xy", node.NewNode(1.0))
		root.MaskPrependChild(parent)
		// Result: a->b->c->x->y (all required).
		Expect(root.String()).To(Equal("Node: ABCXY ◌◌◌◌◌●"))
	})
})

var _ = Describe("RepeatLengthMask", func() {
	It("Repeats path if requested", func() {
		root := node.NewNode()
		root.MaskPathToChild("abcd", node.NewNode(1.0))
		root.RepeatLengthMask(4)
		Expect(root.String()).To(Equal(
			"Node: ABCD ◌◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌◌●◌◌●···"))
	})

	It("Repeats path infinitely when length is -1", func() {
		root := node.NewNode()
		root.MaskPathToChild("abcd", node.NewNode(1.0))
		root.MaskPathToChild("ab", node.NewNode(1.0))
		root.RepeatLengthMask(-1)
		Expect(root.String()).To(Equal(
			"Node: ABcd ◌◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●◌●●···"))
	})
})

var _ = Describe("Union", func() {
	It("Empty nodes are a no-op", func() {
		source := node.NewNode()
		result := node.NewNode().Union(source)
		Expect(result.String()).To(Equal("Node"))
	})

	It("Inherits from source", func() {
		source := node.NewNode()
		source.MaskPath("abc")
		result := node.NewNode().Union(source)
		Expect(result.String()).To(Equal("Node: ABC ◌◌◌●"))
	})

	It("Inherits max weight", func() {
		source := node.NewNode(1)
		result := node.NewNode(.5).Union(source)
		Expect(result.String()).To(Equal("Node: 100 ●"))
	})
})

var _ = Describe("Intersection", func() {
	It("Empty nodes are a no-op", func() {
		source := node.NewNode()
		result := node.NewNode().Intersection(source)
		Expect(result.String()).To(Equal("Node"))
	})

	It("Intersects with source", func() {
		source := node.NewNode()
		source.MaskPath("abb")
		result := node.NewNode()
		result.MaskPath("aab")
		result.Intersection(source)
		Expect(result.String()).To(Equal("Node: AB ◌◌◌●"))
	})

	It("Detects impossible combinations", func() {
		source := node.NewNode()
		source.MaskPath("bcd")
		result := node.NewNode()
		result.MaskPath("abc")
		result.Intersection(source)
		Expect(result.String()).To(Equal("Node: ⒶBCⒹ"))
	})

	It("Inherits max (min) weight", func() {
		source := node.NewNode(.5)
		result := node.NewNode(1).Intersection(source)
		Expect(result.String()).To(Equal("Node: 50 ●"))
	})

	It("Blocks exits if other node has none", func() {
		source := node.NewNode(.5)
		result := node.NewNode(1)
		result.MaskPath("abc")
		Expect(result.String()).To(Equal("Node: 100 ABC ●◌◌●"))
		result.Intersection(source)
		Expect(result.String()).To(Equal("Node: 50 ●"))
	})
})

var _ = Describe("String", func() {
	It("Formats empty Nodes", func() {
		n := node.NewNode()
		Expect(n.String()).To(Equal("Node"))
	})

	It("Formats full Nodes", func() {
		n := node.Node{
			RequireMask: mask.ALL,
			ProvideMask: mask.ALL,
			LengthsMask: mask.Mask(0b1010101),
			MatchWeight: 1.0,
		}
		Expect(n.String()).To(Equal("Node: 100 ABCDEFGHIJKLMNOPQRSTUVWXYZ␣-' ●◌●◌●◌●"))
	})
})

var _ = Describe("NodeIterator", func() {
	It("Has no children", func() {
		n := node.NewNode()
		Expect(n.HasNext()).To(BeFalse())
		items := node.NodeAcceptAll.Items(n)
		Expect(items.HasNext()).To(BeFalse())
	})

	It("Formats empty children", func() {
		n := node.NewNode()
		Expect(debug.StringChildren(n)).To(Equal("Node"))
	})
})
