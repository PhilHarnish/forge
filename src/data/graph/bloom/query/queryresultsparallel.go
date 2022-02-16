package query

/*
Implements:
```
	SELECT
		a, b, c, ..., n
	FROM a, b, c, ..., n
	ORDER BY a * b * c * ... * n DESC
```
...where `a`, `b`, `c`, ... `n` provide monotonically decreasing values.
*/

import (
	"container/heap"

	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type queryResultsParallel struct {
	query       *Query
	sources     []QueryResults
	sourceRows  [][]QueryRow
	maxResult   weight.Weight
	sourceHeap  queryRowResultsRowHeap
	resultsHeap QueryRows
}

type queryRowResultsRow struct {
	row   QueryRow
	value float64
	index int
}

type queryRowResultsRowHeap []*queryRowResultsRow

func (results *queryResultsParallel) HasNext() bool {
	results.init()
	return len(results.resultsHeap) > 0 || len(results.sourceHeap) > 0
}

func (results *queryResultsParallel) Next() QueryRow {
	results.init()
	for {
		potentialRow := results.maybeReturnRow()
		if potentialRow != nil {
			return potentialRow
		}
		nextBestResult := results.takeFromSource()
		if nextBestResult != nil {
			reference := NewQueryRowForQuery(results.query)
			reference.AssignCells(nextBestResult.index, 1.0, nextBestResult.row.Cells())
			results.accumulateQueryRow(reference, nextBestResult.index, 0)
		}
	}
}

func (results *queryResultsParallel) String() string {
	return resultsString(results.query.Header(), results)
}

func (results *queryResultsParallel) accumulateQueryRow(
	reference QueryRow, skipRow int, index int) {
	if skipRow == index {
		// Skip the bestResult row.
		index++
	}
	if index >= len(results.sourceRows) {
		// End of recursion reached.
		results.resultsHeap.Insert(reference.Copy())
		return
	}
	initialWeight := reference.Weight()
	for _, sourceRow := range results.sourceRows[index] {
		reference.AssignCells(index, initialWeight, sourceRow.Cells())
		results.accumulateQueryRow(reference, skipRow, index+1)
	}
}

func (results *queryResultsParallel) init() {
	if results.query == nil || results.sources != nil {
		return
	}
	// 0. Initialize sources.
	nSources := len(results.query.sources)
	results.sources = make([]QueryResults, nSources)
	for index, source := range results.query.sources {
		sourceResults := source.Results()
		results.sources[index] = sourceResults
		if !sourceResults.HasNext() {
			// Unsatisfiable.
			results.query = nil
			results.sources = nil
			return
		}
	}
	results.sourceRows = make([][]QueryRow, nSources)
	// 1. Enqueue the first result.
	firstResultRow := NewQueryRowForQuery(results.query)
	for index, source := range results.sources {
		// Initialize source rows.
		result := source.Next()
		results.sourceRows[index] = []QueryRow{result}
		firstResultRow.AssignCells(index, firstResultRow.weight, result.Cells())
	}
	results.maxResult = firstResultRow.weight
	results.resultsHeap = QueryRows{firstResultRow}
	// 2. Prime the heap with more.
	results.sourceHeap = []*queryRowResultsRow{}
	for index := range results.sources {
		results.pushFromSource(index)
	}
}

func (results *queryResultsParallel) maybeReturnRow() QueryRow {
	nextResultIsValid := len(results.resultsHeap) > 0
	// Determine the newest "valid" result from the best source.
	if nextResultIsValid && len(results.sourceHeap) > 0 {
		// We can only ensure results are optimal when the next best source
		// is guaranteed to generate an inferior result.
		nextResultIsValid = results.resultsHeap[0].Weight() > (results.maxResult * results.sourceHeap[0].value)
	}
	if nextResultIsValid {
		return results.resultsHeap.Next()
	}
	return nil
}

func (results *queryResultsParallel) takeFromSource() *queryRowResultsRow {
	if len(results.sourceHeap) == 0 {
		return nil
	}
	result := results.sourceHeap.Next()
	index := result.index
	results.sourceRows[index] = append(results.sourceRows[index], result.row)
	results.pushFromSource(index)
	return result
}

func (results *queryResultsParallel) pushFromSource(index int) {
	source := results.sources[index]
	if source.HasNext() {
		maxSourceWeight := results.sourceRows[index][0].Weight()
		sourceNext := source.Next()
		heap.Push(&results.sourceHeap, &queryRowResultsRow{
			row:   sourceNext,
			value: sourceNext.Weight() / maxSourceWeight,
			index: index,
		})
	}
}

func (h queryRowResultsRowHeap) Len() int {
	return len(h)
}

func (h queryRowResultsRowHeap) Less(i int, j int) bool {
	return h[i].value > h[j].value
}

func (h queryRowResultsRowHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *queryRowResultsRowHeap) Push(item interface{}) {
	*h = append(*h, item.(*queryRowResultsRow))
}

func (h *queryRowResultsRowHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *queryRowResultsRowHeap) Next() *queryRowResultsRow {
	return heap.Pop(h).(*queryRowResultsRow)
}
