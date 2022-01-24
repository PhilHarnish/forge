package benchmarks_test

import (
	"testing"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

const DEPTH = 6

func BenchmarkLinkingNode(b *testing.B) {
	b.Run("deep", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill(1, 1, trie.NewTrie(1.0))
		}
	})
	b.Run("shallow", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill(1, mask.SIZE, trie.NewTrie(1.0))
		}
	})
	b.Run("full", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill(DEPTH, mask.SIZE/12, trie.NewTrie(1.0))
		}
	})
}

func fill(remaining int, width int, parent *trie.Trie) {
	remaining--
	for i := width - 1; i >= 0; i-- {
		c := mask.ALPHABET[i]
		// Link children with monotonically increasing weights.
		// This will force "expensive" sorting.
		next := trie.NewTrie(1.0 - float64(i)/float64(mask.SIZE))
		parent.Link(string(c), next)
		if remaining > 0 {
			fill(remaining, width, next)
		}
	}
}
