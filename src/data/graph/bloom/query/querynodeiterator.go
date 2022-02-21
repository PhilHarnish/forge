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

func queryNodeIterator(iterator node.NodeIterator) QueryResultsSource {
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
	return []string{"Text"}
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
	if iterator.Root().Matches() {
		results.resultsQueue.Insert(newQueryNodeQueryRow(parent, iterator.Root().MatchWeight, path))
	}
	items := iterator.Items(node.NodeAcceptAll)
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

func newQueryNodeQueryRow(cursor *queryNodeCursor, weight weight.Weight, suffix string) QueryRow {
	// Join the paths to make the string.
	end := len(suffix)
	idx := cursor
	for idx != nil {
		end += len(idx.path)
		idx = idx.parent
	}
	path := make([]byte, end)
	idx = cursor
	copy(path[end-len(suffix):end], []byte(suffix))
	end -= len(suffix)
	for idx != nil {
		if len(idx.path) > 0 {
			copy(path[end-len(idx.path):end], []byte(idx.path))
			end -= len(idx.path)
		}
		idx = idx.parent
	}
	cell := QueryRowCell{
		Weight: weight,
		String: string(path),
	}
	return NewQueryRow([]QueryRowCell{cell})
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

type queryNodeQueryRow struct {
	cells []weight.WeightedString
}

func NewQueryNodeQueryRow() *queryNodeQueryRow {
	return &queryNodeQueryRow{
		cells: make([]weight.WeightedString, 1),
	}
}

func (row *queryNodeQueryRow) Weight() weight.Weight {
	return row.cells[0].Weight
}

func (row *queryNodeQueryRow) Cells() []QueryRowCell {
	return row.cells
}

func (row *queryNodeQueryRow) Copy() QueryRow {
	result := &queryRowForQuery{
		cells: make([]weight.WeightedString, len(row.cells)),
	}
	copy(result.cells, row.cells)
	return result
}

func (row *queryNodeQueryRow) AssignCells(index int, baseWeight weight.Weight, cells []QueryRowCell) {
	copy(row.cells[index:index+len(cells)], cells)
}
