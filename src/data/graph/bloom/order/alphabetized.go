package order

import (
	"container/heap"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type alphabetized struct {
	child node.NodeIterator
}

type alphabetizedItems struct {
	items     node.NodeItems
	remaining alphabetizedHeap
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

func (root *alphabetized) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return &alphabetizedItems{
		items:     root.child.Items(acceptor),
		remaining: alphabetizedHeap{},
	}
}

func (root *alphabetizedItems) HasNext() bool {
	return len(root.remaining) > 0 || root.items.HasNext()
}

func (root *alphabetizedItems) Next() (string, node.NodeIterator) {
	if len(root.remaining) == 0 {
		for root.items.HasNext() {
			path, item := root.items.Next()
			root.remaining = append(root.remaining, &alphabetizedItem{
				path: path,
				item: item,
			})
			heap.Init(&root.remaining)
		}
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
