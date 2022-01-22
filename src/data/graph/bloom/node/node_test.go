package node_test

import (
	"fmt"
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

func TestNode(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Mask tests")
}

var _ = Describe("Match",
	func() {
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

var _ = Describe("Link",
	func() {
		var root *node.Node

		BeforeEach(func() {
			root = node.NewNode()
		})

		It("Linked child is indicated in output",
			func() {
				err := root.Link("c", node.NewNode(1.0))
				Expect(err).ShouldNot(HaveOccurred())
				Expect(root.String()).To(Equal("Node('C', ' #', 0)"))
			})

		It("Rejects empty links",
			func() {
				err := root.Link("", node.NewNode(1.0))
				Expect(err).Should(HaveOccurred())
			})

		It("Rejects illegal links",
			func() {
				err := root.Link("🚫", node.NewNode(1.0))
				Expect(err).Should(MatchError(
					"error while linking: '🚫' not supported"))
			})

		It("Rejects duplicate links",
			func() {
				err := root.Link("c", node.NewNode(1.0))
				Expect(err).ShouldNot(HaveOccurred())
				err = root.Link("c", node.NewNode(1.0))
				Expect(err).Should(MatchError("link 'c' already exists"))
			})

		It("Accepts multi-rune links",
			func() {
				err := root.Link("abc", node.NewNode(1.0))
				Expect(err).ShouldNot(HaveOccurred())
				Expect(root.String()).To(Equal("Node('ABC', '   #', 0)"))
			})

		It("Multiple links eliminate requirement for parent",
			func() {
				for _, c := range "abc" {
					err := root.Link(string(c), node.NewNode(1.0))
					Expect(err).ShouldNot(HaveOccurred())
				}
				Expect(root.String()).To(Equal("Node('abc', ' #', 0)"))
			})

		It("Requirements are inherited",
			func() {
				cursor := node.NewNode(1.0)
				for _, c := range []string{
					"a=Node('A', ' #', 0)",
					"b=Node('AB', '  #', 0)",
					"c=Node('ABC', '   #', 0)",
					"a=Node('ABC', '    #', 0)",
				} {
					next := node.NewNode()
					err := next.Link(string(c[0]), cursor)
					cursor = next
					Expect(err).ShouldNot(HaveOccurred())
					Expect(fmt.Sprintf("%c=%s", c[0], cursor)).To(Equal(c))
				}
			})
	})

var _ = Describe("Satisfies",
	func() {
		It("Empty nodes do not satisfy by default (no exits)",
			func() {
				node := node.NewNode(1.0)
				Expect(node.Satisfies(node)).To(BeFalse())
			})

		It("Fully populated node satisfies anything",
			func() {
				populated := node.NewNode()
				for _, c := range mask.ALPHABET {
					populated.Link(string(c), node.NewNode(1.0))
				}
				for _, c := range mask.ALPHABET {
					seeker := node.NewNode()
					seeker.Link(string(c), node.NewNode(1.0))
					Expect(populated.Satisfies(seeker)).To(BeTrue())
				}
			})
	})
