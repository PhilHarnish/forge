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

func newQueryRowHeaderForSources(
	sources []QueryResultsSource, sourceNames map[int]string) *queryRowHeader {
	result := &queryRowHeader{
		labels:  make([]string, len(sources)),
		offsets: make([]int, len(sources)+1),
	}
	position := 0
	for _, source := range sources {
		name, exists := sourceNames[position]
		if !exists {
			name = source.String()
		}
		childLabels := source.Header().Labels()
		if len(childLabels) == 1 {
			result.labels[position] = name
			result.offsets[position] = position
			position++
		} else {
			for _, childLabel := range childLabels {
				result.labels[position] = name + "." + childLabel
				result.offsets[position] = position
				position++
			}
		}
		// Set one last offset for the OOB location.
		result.offsets[position] = position
	}
	return result
}

type QueryRow interface {
	Weight() weight.Weight
	Cells() []QueryRowCell
	Copy() QueryRow
	ReplaceSource(index int, cells []weight.WeightedString)
}

type QueryRowCell = weight.WeightedString

type queryRowFromSources struct {
	query  *Query
	weight weight.Weight
	cells  []weight.WeightedString
}

func NewQueryRowFromQueryResults(query *Query, sources []QueryResults) *queryRowFromSources {
	cells := make([]QueryRowCell, len(query.getColumnHeader().labels))
	index := 0
	for _, source := range sources {
		result := source.Next()
		sourceCells := result.Cells()
		copy(cells[index:index+len(sourceCells)], sourceCells)
		index += len(sourceCells)
	}
	if index != len(query.getColumnHeader().labels) {
		panic(fmt.Sprintf("Query requires %d cells, %d provided",
			len(query.getColumnHeader().labels), len(cells)))
	}
	return &queryRowFromSources{
		query:  query,
		weight: weight.CumulativeWeight(cells),
		cells:  cells,
	}
}

func NewQueryRowFromCells(query *Query, cells []weight.WeightedString) *queryRowFromSources {
	if len(cells) != len(query.getColumnHeader().labels) {
		panic(fmt.Sprintf("Query requires %d cells, %d provided",
			len(query.getColumnHeader().labels), len(cells)))
	}
	return &queryRowFromSources{
		query:  query,
		weight: weight.CumulativeWeight(cells),
		cells:  cells,
	}
}

func (row *queryRowFromSources) Weight() weight.Weight {
	return row.weight
}

func (row *queryRowFromSources) Cells() []QueryRowCell {
	return row.cells
}

func (row *queryRowFromSources) Copy() QueryRow {
	result := &queryRowFromSources{
		query:  row.query,
		weight: row.weight,
		cells:  make([]weight.WeightedString, len(row.cells)),
	}
	copy(result.cells, row.cells)
	return result
}

func (row *queryRowFromSources) ReplaceSource(index int, cells []weight.WeightedString) {
	header := row.query.getColumnHeader()
	columnStart := header.offsets[index]
	columnEnd := header.offsets[index+1]
	if columnStart+len(cells) != columnEnd {
		panic(fmt.Sprintf("Column %d is %d cells wide: [%d, %d); given %d items",
			index, columnEnd-columnStart, columnStart, columnEnd, len(cells)))
	}
	oldWeight := weight.CumulativeWeight(row.cells[columnStart:columnEnd])
	newWeight := weight.CumulativeWeight(cells)
	row.weight = newWeight * row.weight / oldWeight
	copy(row.cells[columnStart:columnEnd], cells)
}
