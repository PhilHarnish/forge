package trie

import (
	"github.com/philharnish/forge/src/data/graph/bloom/cursor"
	"github.com/philharnish/forge/src/data/graph/bloom/iterator"
)

type iteratorItems struct {
	heap []*cursor.Cursor
}

func newIteratorItems(trie *Trie) *iteratorItems {
	return &iteratorItems{
		heap: []*cursor.Cursor{
			cursor.NewCursor(trie),
		},
	}
}

func (items *iteratorItems) Next() *iterator.IteratorItem {
	return nil
}
