package bloom_test

import (
	"fmt"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom"
)

var _ = Describe("Match",
	func() {
		It("Initially does not match", func() {
			node := bloom.NewNode()
			Expect(node.String()).To(Equal("Node('', '', 0)"))
		})

		It("Match indicated in String output", func() {
			node := bloom.NewNode()
			node.Match(0.5)
			Expect(node.String()).To(Equal("Node('', '#', 0.5)"))
		})

		It("Rejects duplicate attempts", func() {
			node := bloom.NewNode()
			node.Match(0.5)
			Expect(func() {
				node.Match(0.5)
			}).To(Panic())
		})
	})

var _ = Describe("Link",
	func() {
		var node *bloom.Node

		BeforeEach(func() {
			node = bloom.NewNode()
		})

		It("Linked child is indicated in output",
			func() {
				err := node.Link("c", bloom.NewNode(1.0))
				Expect(err).ShouldNot(HaveOccurred())
				Expect(node.String()).To(Equal("Node('C', ' #', 0)"))
			})

		It("Rejects empty links",
			func() {
				err := node.Link("", bloom.NewNode(1.0))
				Expect(err).Should(HaveOccurred())
			})

		It("Rejects illegal links",
			func() {
				err := node.Link("🚫", bloom.NewNode(1.0))
				Expect(err).Should(MatchError(
					"error while linking: '🚫' not supported"))
			})

		It("Rejects duplicate links",
			func() {
				err := node.Link("c", bloom.NewNode(1.0))
				Expect(err).ShouldNot(HaveOccurred())
				err = node.Link("c", bloom.NewNode(1.0))
				Expect(err).Should(MatchError("link 'c' already exists"))
			})

		It("Multiple links eliminate requirement for parent",
			func() {
				for _, c := range "abc" {
					err := node.Link(string(c), bloom.NewNode(1.0))
					Expect(err).ShouldNot(HaveOccurred())
				}
				Expect(node.String()).To(Equal("Node('abc', ' #', 0)"))
			})

		It("Requirements are inherited",
			func() {
				cursor := bloom.NewNode(1.0)
				for _, c := range []string{
					"a=Node('A', ' #', 0)",
					"b=Node('AB', '  #', 0)",
					"c=Node('ABC', '   #', 0)",
					"a=Node('ABC', '    #', 0)",
				} {
					next := bloom.NewNode()
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
				node := bloom.NewNode(1.0)
				Expect(node.Satisfies(node)).To(BeFalse())
			})

		It("Fully populated node satisfies anything",
			func() {
				populated := bloom.NewNode()
				for _, c := range bloom.ALPHABET {
					populated.Link(string(c), bloom.NewNode(1.0))
				}
				for _, c := range bloom.ALPHABET {
					seeker := bloom.NewNode()
					seeker.Link(string(c), bloom.NewNode(1.0))
					Expect(populated.Satisfies(seeker)).To(BeTrue())
				}
			})
	})
