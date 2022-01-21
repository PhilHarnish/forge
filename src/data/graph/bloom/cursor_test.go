package bloom_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom"
)

var _ = Describe("Cursor",
	func() {
		It("Initially empty", func() {
			node := bloom.NewNode()
			cursor := bloom.NewCursor(node)
			Expect(cursor.String()).To(Equal("Cursor('', Node('', '', 0))"))
		})

		It("Moves to children", func() {
			node := bloom.NewNode()
			cursor := bloom.NewCursor(node)
			cursor.Get("abc")
			Expect(cursor.String()).To(Equal("Cursor('abc', Node('', '', 0))"))
		})

		It("Moves to children iteratively", func() {
			node := bloom.NewNode()
			cursor := bloom.NewCursor(node)
			for _, c := range "abc" {
				cursor.Get(string(c))
			}
			Expect(cursor.String()).To(Equal("Cursor('abc', Node('', '', 0))"))
		})
	})
