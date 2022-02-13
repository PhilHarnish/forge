package query

import (
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

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
		if !exists {
			name = fmt.Sprintf("_%d", sourceIndex)
		}
		childLabels := source.Header().Labels()
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

type QueryRow interface {
	Weight() weight.Weight
	Cells() []QueryRowCell
	Copy() QueryRow
	AssignCells(index int, baseWeight weight.Weight, cells []QueryRowCell)
}

type QueryRowCell = weight.WeightedString

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
