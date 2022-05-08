package query

import (
	"container/heap"
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type queryNodeResultsSource struct {
	iterator node.NodeIterator
}

type queryNodeResults struct {
	source       *queryNodeResultsSource
	resultsQueue QueryRows
	fringe       queryNodeFringe
}

type queryNodeCursor struct {
	parent *queryNodeCursor
	value  weight.Weight
	path   string
	items  node.NodeItems
}

type queryNodeFringe []*queryNodeCursor

func newQueryNodeResultsSource(iterator node.NodeIterator) QueryResultsSource {
	return &queryNodeResultsSource{iterator: iterator}
}

func (source *queryNodeResultsSource) Results() QueryResults {
	results := &queryNodeResults{
		source: source,
		fringe: queryNodeFringe{},
	}
	results.maybeExpandIterator(nil, "", source.iterator)
	return results
}

func (source *queryNodeResultsSource) String(includeResults ...bool) string {
	return fmt.Sprintf("(%s)", source.iterator.String())
}

func (source *queryNodeResultsSource) Header() QueryRowHeader {
	return source
}

func (source *queryNodeResultsSource) Labels() []string {
	labels := []string{"Text"}
	iteratorHeaderProvider, hasHeader := source.iterator.(QueryHeaderProvider)
	if hasHeader {
		labels = append(labels, iteratorHeaderProvider.Header().Labels()...)
	}
	return labels
}

func (results *queryNodeResults) HasNext() bool {
	if len(results.resultsQueue) > 0 {
		return true
	}
	for len(results.fringe) > 0 {
		results.maybeContinueIteration(results.fringe.Next())
	}
	return len(results.resultsQueue) > 0
}

func (results *queryNodeResults) Next() QueryRow {
	return results.resultsQueue.Next()
}

func (results *queryNodeResults) String() string {
	return resultsString(results.source.Header(), results)
}

func (results *queryNodeResults) maybeExpandIterator(
	parent *queryNodeCursor, path string, iterator node.NodeIterator) {
	items := node.NodeGenerateAll.Items(iterator)
	if iterator.Root().Matches() {
		results.resultsQueue.Insert(results.newQueryNodeQueryRow(parent, iterator.Root().MatchWeight, path, items))
	}
	if items.HasNext() {
		heap.Push(&results.fringe, &queryNodeCursor{
			parent: parent,
			value:  iterator.Root().MaxWeight,
			path:   path,
			items:  items,
		})
	}
}

func (results *queryNodeResults) maybeContinueIteration(parent *queryNodeCursor) {
	parentItems := parent.items
	childPath, childIterator := parentItems.Next()
	results.maybeExpandIterator(parent, childPath, childIterator)
	// If there are more items, continue iteration.
	if parentItems.HasNext() {
		// Lower value to the value most recently returned.
		parent.value = childIterator.Root().MaxWeight
		heap.Push(&results.fringe, parent)
	}
}

func (results *queryNodeResults) newQueryNodeQueryRow(
	cursor *queryNodeCursor, weight weight.Weight, suffixPath string, suffixItems node.NodeItems) QueryRow {
	metadataProvider, isProvider := results.source.iterator.(node.NodeMetadataProvider)
	// Join the paths to make the string.
	count := 0
	end := len(suffixPath)
	idx := cursor
	for idx != nil {
		end += len(idx.path)
		count++
		idx = idx.parent
	}
	path := make([]byte, end)
	var pathList []string
	var itemList []node.NodeItems
	idx = cursor
	copy(path[end-len(suffixPath):end], []byte(suffixPath))
	if isProvider {
		pathList = make([]string, count)
		itemList = make([]node.NodeItems, count+1)
		count--
		itemList[count+1] = suffixItems
		pathList[count] = suffixPath
	}
	end -= len(suffixPath)
	for idx != nil {
		if len(idx.path) > 0 {
			copy(path[end-len(idx.path):end], []byte(idx.path))
			end -= len(idx.path)
		}
		if isProvider {
			count--
			itemList[count+1] = idx.items
			if count >= 0 {
				pathList[count] = idx.path
			}
		}
		idx = idx.parent
	}
	pathResult := string(path)
	cells := []QueryRowCell{{
		Weight: weight,
		String: pathResult,
	}}
	if isProvider {
		cells = append(cells, metadataProvider.Metadata(pathList, itemList)...)
	}
	return NewQueryRow(cells)
}

func (h queryNodeFringe) Len() int {
	return len(h)
}

func (h queryNodeFringe) Less(i int, j int) bool {
	return h[i].value > h[j].value
}

func (h queryNodeFringe) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *queryNodeFringe) Push(item interface{}) {
	*h = append(*h, item.(*queryNodeCursor))
}

func (h *queryNodeFringe) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *queryNodeFringe) Next() *queryNodeCursor {
	return heap.Pop(h).(*queryNodeCursor)
}
