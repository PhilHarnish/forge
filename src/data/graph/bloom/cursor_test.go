package bloom_test

import (
	"errors"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom"
)

func extend(node *bloom.Node, paths ...string) *bloom.Node {
	for i := len(paths) - 1; i >= 0; i-- {
		parent := bloom.NewNode()
		err := parent.Link(paths[i], node)
		Expect(err).ShouldNot(HaveOccurred())
		node = parent
	}
	return node
}

var _ = Describe("Cursor.NewNode",
	func() {
		It("Initially empty", func() {
			node := extend(bloom.NewNode(1.0), "a", "b", "c")
			cursor := bloom.NewCursor(node)
			Expect(cursor.String()).To(Equal("Cursor('', Node('ABC', '   #', 0))"))
		})
	})

var _ = Describe("Cursor.Get",
	func() {
		It("Moves to children", func() {
			node := extend(bloom.NewNode(1.0), "a", "b", "c")
			cursor := bloom.NewCursor(node)
			_, err := cursor.Get("abc")
			Expect(err).ShouldNot(HaveOccurred())
			Expect(cursor.String()).To(Equal("Cursor('abc', Node('', '#', 1))"))
		})

		It("Moves to children iteratively", func() {
			node := extend(bloom.NewNode(1.0), "a", "b", "c")
			cursor := bloom.NewCursor(node)
			for _, c := range "abc" {
				_, err := cursor.Get(string(c))
				Expect(err).ShouldNot(HaveOccurred())
			}
			Expect(cursor.String()).To(Equal("Cursor('abc', Node('', '#', 1))"))
		})

		It("Moves to virtual child with prefix", func() {
			node := bloom.NewNode()
			Expect(node.Link("abc", bloom.NewNode(1.0))).ShouldNot(HaveOccurred())
			cursor := bloom.NewCursor(node)
			_, err := cursor.Get("abc")
			Expect(err).ShouldNot(HaveOccurred())
			Expect(cursor.String()).To(Equal("Cursor('abc', Node('', '#', 1))"))
		})

		It("Moves across bridge", func() {
			node := extend(bloom.NewNode(1.0), "a", "bridge", "z")
			cursor := bloom.NewCursor(node)
			_, err := cursor.Get("abridgez")
			Expect(err).ShouldNot(HaveOccurred())
			Expect(cursor.String()).To(Equal("Cursor('abridgez', Node('', '#', 1))"))
		})

		It("Errors when exhausting path while on bridge", func() {
			node := extend(bloom.NewNode(1.0), "a", "bridge", "z")
			cursor := bloom.NewCursor(node)
			_, err := cursor.Get("abri")
			Expect(err).Should(MatchError(
				"Cursor('a', Node('BDEGIRZ', '       #', 0)) traversal error for 'abri': exhausted input traversing prefix 'ridge' on Node('BDEGIRZ', '       #', 0)[b]"))
		})

		It("Errors when leaving bridge early", func() {
			node := extend(bloom.NewNode(1.0), "a", "bridge", "z")
			cursor := bloom.NewCursor(node)
			_, err := cursor.Get("abriz")
			Expect(err).Should(MatchError(
				"Cursor('a', Node('BDEGIRZ', '       #', 0)) traversal error for 'abriz': prefix mismatch 'bridge' is not a prefix of 'briz'"))
		})

		It("Raises error attempting to traverse illegal character", func() {
			node := extend(bloom.NewNode(1.0), "abc")
			cursor := bloom.NewCursor(node)
			_, err := cursor.Get("🚫")
			Expect(err).Should(MatchError(
				"Cursor('', Node('ABC', '   #', 0)) traversal error for '🚫': '🚫' not supported",
			))
		})

		It("Raises error attempting to traverse missing character", func() {
			node := extend(bloom.NewNode(1.0), "abc")
			cursor := bloom.NewCursor(node)
			_, err := cursor.Get("xyz")
			Expect(err).Should(MatchError(
				"Cursor('', Node('ABC', '   #', 0)) traversal error for 'xyz': 'XYZ' not provided",
			))
		})

		It("Raises error attempting to traverse out of order", func() {
			node := extend(bloom.NewNode(1.0), "abc")
			cursor := bloom.NewCursor(node)
			_, err := cursor.Get("cba")
			Expect(err).Should(MatchError(
				"Cursor('', Node('ABC', '   #', 0)) traversal error for 'cba': 'c' not linked",
			))
		})
	})

var _ = Describe("Cursor.Select",
	func() {
		It("Moves to children", func() {
			node := extend(bloom.NewNode(1.0), "abc")
			cursor := bloom.NewCursor(node)
			cursor.Select("abc")
			Expect(cursor.String()).To(Equal("Cursor('abc', Node('', '#', 1))"))
		})

		It("Panics when performing an illegal selection", func() {
			node := extend(bloom.NewNode(1.0), "abc")
			cursor := bloom.NewCursor(node)
			Expect(func() {
				cursor.Select("xyz")
			}).To(PanicWith(errors.New("path xyz not found on Node('ABC', '   #', 0)")))
		})
	})
