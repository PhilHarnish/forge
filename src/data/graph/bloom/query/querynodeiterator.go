package query

import (
	"container/heap"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type queryNodeResultsSource struct {
	iterator node.NodeIterator
}

type queryNodeResults struct {
	resultsQueue QueryRows
	fringe       queryNodeFringe
}

type queryNodeCursor struct {
	parent *queryNodeCursor
	path   string
	leaf   node.NodeIterator
}

type queryNodeFringe []*queryNodeCursor

func queryNodeIterator(iterator node.NodeIterator) QueryResultsSource {
	return &queryNodeResultsSource{iterator: iterator}
}

func (source *queryNodeResultsSource) Results() QueryResults {
	return &queryNodeResults{
		fringe: queryNodeFringe{
			{
				leaf: source.iterator,
			},
		},
	}
}

func (source *queryNodeResultsSource) String() string {
	return source.iterator.String()
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
	// <otherwise, look for results>
	for len(results.fringe) > 0 {
		edge := results.fringe.Next()
		if edge.leaf.Root().Matches() {
			results.resultsQueue.Insert(newQueryNodeQueryRow(edge))
			return true
		}
		items := edge.leaf.Items(node.NodeAcceptAll)
		for items.HasNext() {
			results.fringe = append(results.fringe, newQueryNodeCursorFromItems(edge, items))
		}
	}
	return false
}

func (results *queryNodeResults) Next() QueryRow {
	return results.resultsQueue.Next()
}

func newQueryNodeCursorFromItems(parent *queryNodeCursor, items node.NodeItems) *queryNodeCursor {
	path, iterator := items.Next()
	return &queryNodeCursor{
		parent: parent,
		path:   path,
		leaf:   iterator,
	}
}

func newQueryNodeQueryRow(cursor *queryNodeCursor) QueryRow {
	// Join the paths to make the string.
	end := 0
	idx := cursor
	for idx != nil {
		end += len(idx.path)
		idx = idx.parent
	}
	path := make([]byte, end)
	idx = cursor
	for idx != nil {
		copy(path[end-len(idx.path):end], []byte(idx.path))
		end -= len(idx.path)
		idx = idx.parent
	}
	cell := QueryRowCell{
		Weight: cursor.leaf.Root().MatchWeight,
		String: string(path),
	}
	return NewQueryRow([]QueryRowCell{cell})
}

func (h queryNodeFringe) Len() int {
	return len(h)
}

func (h queryNodeFringe) Less(i int, j int) bool {
	return h[i].leaf.Root().MaxWeight > h[j].leaf.Root().MaxWeight
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
