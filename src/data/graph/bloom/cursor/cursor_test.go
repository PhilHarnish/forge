package cursor_test

import (
	"errors"
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/cursor"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

func TestCursor(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Cursor tests")
}

func extend(item *node.Node, paths ...string) *node.Node {
	for i := len(paths) - 1; i >= 0; i-- {
		parent := node.NewNode()
		err := parent.Link(paths[i], item)
		Expect(err).ShouldNot(HaveOccurred())
		item = parent
	}
	return item
}

var _ = Describe("Cursor.NewNode", func() {
	It("Initially empty", func() {
		root := extend(node.NewNode(1.0), "a", "b", "c")
		cursor := cursor.NewCursor(root)
		Expect(cursor.String()).To(Equal("Cursor('', Node('ABC', '   #', 0))"))
	})
})

var _ = Describe("Cursor.Get", func() {
	It("Moves to children", func() {
		root := extend(node.NewNode(1.0), "a", "b", "c")
		cursor := cursor.NewCursor(root)
		_, err := cursor.Get("abc")
		Expect(err).ShouldNot(HaveOccurred())
		Expect(cursor.String()).To(Equal("Cursor('abc', Node('', '#', 1))"))
	})

	It("Moves to children iteratively", func() {
		n := extend(node.NewNode(1.0), "a", "b", "c")
		c := cursor.NewCursor(n)
		for _, path := range "abc" {
			_, err := c.Get(string(path))
			Expect(err).ShouldNot(HaveOccurred())
		}
		Expect(c.String()).To(Equal("Cursor('abc', Node('', '#', 1))"))
	})

	It("Moves to virtual child with prefix", func() {
		n := node.NewNode()
		Expect(n.Link("abc", node.NewNode(1.0))).ShouldNot(HaveOccurred())
		c := cursor.NewCursor(n)
		_, err := c.Get("abc")
		Expect(err).ShouldNot(HaveOccurred())
		Expect(c.String()).To(Equal("Cursor('abc', Node('', '#', 1))"))
	})

	It("Moves across bridge", func() {
		n := extend(node.NewNode(1.0), "a", "bridge", "z")
		c := cursor.NewCursor(n)
		_, err := c.Get("abridgez")
		Expect(err).ShouldNot(HaveOccurred())
		Expect(c.String()).To(Equal("Cursor('abridgez', Node('', '#', 1))"))
	})

	It("Errors when exhausting path while on bridge", func() {
		n := extend(node.NewNode(1.0), "a", "bridge", "z")
		c := cursor.NewCursor(n)
		_, err := c.Get("abri")
		Expect(err).Should(MatchError(
			"Cursor('a', Node('BDEGIRZ', '       #', 0)) traversal error for 'abri': exhausted input traversing prefix 'bridge' on Node('BDEGIRZ', '       #', 0)[b]"))
	})

	It("Errors when leaving bridge early", func() {
		n := extend(node.NewNode(1.0), "a", "bridge", "z")
		c := cursor.NewCursor(n)
		_, err := c.Get("abriz")
		Expect(err).Should(MatchError(
			"Cursor('a', Node('BDEGIRZ', '       #', 0)) traversal error for 'abriz': prefix mismatch 'bridge' is not a prefix of 'briz'"))
	})

	It("Raises error attempting to traverse illegal character", func() {
		n := extend(node.NewNode(1.0), "abc")
		c := cursor.NewCursor(n)
		_, err := c.Get("🚫")
		Expect(err).Should(MatchError(
			"Cursor('', Node('ABC', '   #', 0)) traversal error for '🚫': '🚫' not supported",
		))
	})

	It("Raises error attempting to traverse missing character", func() {
		n := extend(node.NewNode(1.0), "abc")
		c := cursor.NewCursor(n)
		_, err := c.Get("xyz")
		Expect(err).Should(MatchError(
			"Cursor('', Node('ABC', '   #', 0)) traversal error for 'xyz': 'XYZ' not provided",
		))
	})

	It("Raises error attempting to traverse out of order", func() {
		n := extend(node.NewNode(1.0), "abc")
		c := cursor.NewCursor(n)
		_, err := c.Get("cba")
		Expect(err).Should(MatchError(
			"Cursor('', Node('ABC', '   #', 0)) traversal error for 'cba': 'c' not linked",
		))
	})
})

var _ = Describe("Cursor.Select", func() {
	It("Moves to children", func() {
		n := extend(node.NewNode(1.0), "abc")
		c := cursor.NewCursor(n)
		c.Select("abc")
		Expect(c.String()).To(Equal("Cursor('abc', Node('', '#', 1))"))
	})

	It("Panics when performing an illegal selection", func() {
		n := extend(node.NewNode(1.0), "abc")
		c := cursor.NewCursor(n)
		Expect(func() {
			c.Select("xyz")
		}).To(PanicWith(errors.New("path xyz not found on Node('ABC', '   #', 0)")))
	})
})
