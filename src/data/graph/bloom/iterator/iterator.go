package iterator

import (
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type Iterator interface {
	Items() IteratorItems
}

type IteratorItems interface {
	Next() *IteratorItem
}

type IteratorItem struct {
	Item   string
	Weight weight.Weight
}
