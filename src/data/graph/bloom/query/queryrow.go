package query

import (
	"container/heap"
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type QueryRowCell = weight.WeightedString

type QueryRow interface {
	Weight() weight.Weight
	Cells() []QueryRowCell
	Copy() QueryRow
	AssignCells(index int, baseWeight weight.Weight, cells []QueryRowCell)
}

type queryRow struct {
	weight weight.Weight
	cells  []QueryRowCell
}

func NewQueryRow(cells []QueryRowCell) QueryRow {
	return &queryRow{
		weight: weight.CumulativeWeight(cells),
		cells:  cells,
	}
}

func (row *queryRow) Weight() weight.Weight {
	return row.weight
}

func (row *queryRow) Cells() []QueryRowCell {
	return row.cells
}

func (row *queryRow) Copy() QueryRow {
	result := &queryRow{
		weight: row.weight,
		cells:  make([]weight.WeightedString, len(row.cells)),
	}
	copy(result.cells, row.cells)
	return result
}

func (row *queryRow) AssignCells(index int, baseWeight weight.Weight, cells []QueryRowCell) {
	row.weight = baseWeight * weight.CumulativeWeight(cells)
	copy(row.cells[index:index+len(cells)], cells)
}

type QueryRows []QueryRow

type QueryRowHeader interface {
	Labels() []string
}

type queryRowHeader struct {
	labels  []string
	offsets []int
}

func (header *queryRowHeader) Labels() []string {
	return header.labels
}

func newQueryRowHeaderForQuery(query *Query) *queryRowHeader {
	sources := query.sources
	sourceNames := query.sourceNames
	nSources := len(sources)
	result := &queryRowHeader{
		labels:  make([]string, 0, nSources),
		offsets: make([]int, nSources+1),
	}
	position := 0
	for sourceIndex, source := range sources {
		result.offsets[sourceIndex] = len(result.labels)
		name, exists := sourceNames[sourceIndex]
		childLabels := source.Header().Labels()
		if exists {
			// Use alias as name.
		} else if childLabels[0] == "" {
			name = fmt.Sprintf("_%d", sourceIndex)
		} else {
			// Inherit child's name.
			name = childLabels[0]
		}
		if len(childLabels) == 1 {
			result.labels = append(result.labels, name)
			position++
		} else {
			for _, childLabel := range childLabels {
				result.labels = append(result.labels, name+"."+childLabel)
				position++
			}
		}
	}
	result.offsets[nSources] = len(result.labels)
	return result
}

type queryRowForQuery struct {
	query  *Query
	weight weight.Weight
	cells  []weight.WeightedString
}

func NewQueryRowForQuery(query *Query) *queryRowForQuery {
	return &queryRowForQuery{
		query:  query,
		weight: 1.0,
		cells:  make([]weight.WeightedString, len(query.Header().Labels())),
	}
}

func (row *queryRowForQuery) Weight() weight.Weight {
	return row.weight
}

func (row *queryRowForQuery) Cells() []QueryRowCell {
	return row.cells
}

func (row *queryRowForQuery) Copy() QueryRow {
	result := &queryRowForQuery{
		query:  row.query,
		weight: row.weight,
		cells:  make([]weight.WeightedString, len(row.cells)),
	}
	copy(result.cells, row.cells)
	return result
}

func (row *queryRowForQuery) AssignCells(index int, baseWeight weight.Weight, cells []QueryRowCell) {
	row.query.Header()
	header := row.query.header
	columnStart := header.offsets[index]
	columnEnd := header.offsets[index+1]
	if columnStart+len(cells) != columnEnd {
		panic(fmt.Sprintf("Column %d is %d cells wide: [%d, %d); given %d items",
			index, columnEnd-columnStart, columnStart, columnEnd, len(cells)))
	} else if len(cells) == 1 {
		row.cells[columnStart] = cells[0]
		row.weight = baseWeight * cells[0].Weight
	} else {
		copy(row.cells[columnStart:columnEnd], cells)
		row.weight = baseWeight * weight.CumulativeWeight(cells)
	}
}

func (h QueryRows) Len() int {
	return len(h)
}

func (h QueryRows) Less(i int, j int) bool {
	return h[i].Weight() > h[j].Weight()
}

func (h QueryRows) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *QueryRows) Push(item interface{}) {
	*h = append(*h, item.(QueryRow))
}

func (h *QueryRows) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *QueryRows) Next() QueryRow {
	return heap.Pop(h).(QueryRow)
}

func (h *QueryRows) Insert(item QueryRow) {
	heap.Push(h, item)
}
