package order

import (
	"container/heap"
	"math"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type alphabetized struct {
	child node.NodeIterator
}

type alphabetizedItems struct {
	items     node.NodeItems
	remaining alphabetizedHeap
	hasErrors bool
}

type alphabetizedItem struct {
	path string
	item node.NodeIterator
}

type alphabetizedHeap []*alphabetizedItem

func Alphabetized(child node.NodeIterator) node.NodeIterator {
	return &alphabetized{
		child: child,
	}
}

func (root *alphabetized) Root() *node.Node {
	return root.child.Root()
}

func (root *alphabetized) String() string {
	return root.child.String()
}

func (root *alphabetized) Items(generator node.NodeGenerator) node.NodeItems {
	return &alphabetizedItems{
		items:     root.child.Items(generator),
		remaining: alphabetizedHeap{},
	}
}

func (root *alphabetizedItems) HasNext() bool {
	return len(root.remaining) > 0 || root.items.HasNext()
}

func (root *alphabetizedItems) Next() (string, node.NodeIterator) {
	if len(root.remaining) == 0 {
		lastValue := math.Inf(1)
		for root.items.HasNext() {
			path, item := root.items.Next()
			root.remaining = append(root.remaining, &alphabetizedItem{
				path: path,
				item: item,
			})
			currentValue := item.Root().MaxWeight
			if currentValue > lastValue {
				root.hasErrors = true
			}
			lastValue = currentValue
		}
		if !root.hasErrors {
			heap.Init(&root.remaining)
		}
	}
	if root.hasErrors {
		nextItem := root.remaining[0]
		root.remaining = root.remaining[1:]
		return nextItem.path, nextItem.item
	}
	nextItem := root.remaining.Next()
	return nextItem.path, nextItem.item
}

func (h alphabetizedHeap) Len() int {
	return len(h)
}

func (h alphabetizedHeap) Less(i int, j int) bool {
	iWeight := h[i].item.Root().MaxWeight
	jWeight := h[j].item.Root().MaxWeight
	if iWeight == jWeight {
		return h[i].path < h[j].path
	}
	return iWeight >= jWeight
}

func (h alphabetizedHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *alphabetizedHeap) Push(item interface{}) {
	*h = append(*h, item.(*alphabetizedItem))
}

func (h *alphabetizedHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *alphabetizedHeap) Next() *alphabetizedItem {
	return heap.Pop(h).(*alphabetizedItem)
}
