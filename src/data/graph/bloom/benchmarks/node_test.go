package benchmarks_test

import (
	"testing"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

const DEPTH = 6

func BenchmarkLinkingNode(b *testing.B) {
	b.Run("deep", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill(1, 1, node.NewNode(1.0))
		}
	})
	b.Run("shallow", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill(1, mask.SIZE, node.NewNode(1.0))
		}
	})
	b.Run("full", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill(DEPTH, mask.SIZE/12, node.NewNode(1.0))
		}
	})
}

func fill(remaining int, width int, parent *node.Node) {
	remaining--
	for i := width - 1; i >= 0; i-- {
		c := mask.ALPHABET[i]
		// Link children with monotonically increasing weights.
		// This will force "expensive" sorting.
		next := node.NewNode(1.0 - float64(i)/float64(mask.SIZE))
		parent.Link(string(c), next)
		if remaining > 0 {
			fill(remaining, width, next)
		}
	}
}
func BenchmarkLinkingNode2(b *testing.B) {
	b.Run("deep", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill2(1, 1, node.NewNode2(1.0))
		}
	})
	b.Run("shallow", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill2(1, mask.SIZE, node.NewNode2(1.0))
		}
	})
	b.Run("full", func(b *testing.B) {
		for x := b.N; x >= 0; x-- {
			fill2(DEPTH, mask.SIZE/12, node.NewNode2(1.0))
		}
	})
}

func fill2(remaining int, width int, parent *node.Node2) {
	remaining--
	for i := width - 1; i >= 0; i-- {
		c := mask.ALPHABET[i]
		// Link children with monotonically increasing weights.
		// This will force "expensive" sorting.
		next := node.NewNode2(1.0 - float64(i)/float64(mask.SIZE))
		parent.Link(string(c), next)
		if remaining > 0 {
			fill2(remaining, width, next)
		}
	}
}
