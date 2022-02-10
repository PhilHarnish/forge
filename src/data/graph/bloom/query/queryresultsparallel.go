package query

import (
	"container/heap"
)

// TODO: Compare the performance of...
// 1. Store the results returned from each stream and prepare cross-product on demand.
// 2. Store the final results returned overall and iterate those directly.

type queryResultsParallel struct {
	query       *Query
	sources     []QueryResults
	output      queryResultsParallelHeap
	sourceHeap  queryResultsParallelHeap
	resultsHeap queryResultsParallelHeap
}

type queryRowGeneration struct {
	row        QueryRow
	generation int
	index      int
}

type queryResultsParallelHeap []*queryRowGeneration

func (results *queryResultsParallel) HasNext() bool {
	results.init()
	return len(results.resultsHeap) > 0 || len(results.sourceHeap) > 0
}

func (results *queryResultsParallel) Next() QueryRow {
	results.init()
	for {
		potentialRow := results.maybeReturnRow()
		if potentialRow != nil {
			results.output = append(results.output, potentialRow)
			return potentialRow.row
		}
		nextBestResult := results.takeFromSource()
		if nextBestResult != nil {
			newResults := queryResultsParallelHeap{}
			for _, oldResult := range results.output {
				if oldResult.index == nextBestResult.index {
					continue
				}
				newResult := &queryRowGeneration{
					row:        oldResult.row.Copy(),
					generation: nextBestResult.generation,
					index:      nextBestResult.index,
				}
				newResult.row.ReplaceSource(nextBestResult.index, nextBestResult.row.Cells())
				newResults = append(newResults, newResult)
			}
			for _, oldResult := range results.resultsHeap {
				if oldResult.index == nextBestResult.index {
					continue
				}
				newResult := &queryRowGeneration{
					row:        oldResult.row.Copy(),
					generation: nextBestResult.generation,
					index:      nextBestResult.index,
				}
				newResult.row.ReplaceSource(nextBestResult.index, nextBestResult.row.Cells())
				newResults = append(newResults, newResult)
			}
			for _, newResult := range newResults {
				heap.Push(&results.resultsHeap, newResult)
			}
			if len(results.resultsHeap) == 0 && len(results.sourceHeap) == 0 {
				panic("results exhausted")
			}
		}
	}
}

func (results *queryResultsParallel) init() {
	if results.sources != nil {
		return
	}
	// 0. Initialize sources.
	results.sources = make([]QueryResults, len(results.query.sources))
	for index, source := range results.query.sources {
		sourceResults := source.Results()
		results.sources[index] = sourceResults
		if !sourceResults.HasNext() {
			return // Unsatisfiable.
		}
	}
	// 1. Enqueue the first result.
	results.resultsHeap = []*queryRowGeneration{
		{
			row:        NewQueryRowFromQueryResults(results.query, results.sources),
			generation: 0,
			index:      -1,
		},
	}
	// 2. Prime the heap with more.
	results.sourceHeap = []*queryRowGeneration{}
	for index := range results.sources {
		results.pushFromSource(index, 1) // These are the 2nd (`1`) values returned.
	}
}

func (results *queryResultsParallel) maybeReturnRow() *queryRowGeneration {
	nextResultIsValid := len(results.resultsHeap) > 0
	// Determine the newest "valid" result from the best source.
	if nextResultIsValid && len(results.sourceHeap) > 0 {
		// We can only ensure results are optimal when the results are older
		// than the next-best source.
		nextResultIsValid = results.resultsHeap[0].generation < results.sourceHeap[0].generation
	}
	if nextResultIsValid {
		return results.resultsHeap.Next()
	}
	return nil
}

func (results *queryResultsParallel) takeFromSource() *queryRowGeneration {
	if len(results.sourceHeap) == 0 {
		return nil
	}
	result := results.sourceHeap.Next()
	source := results.sources[result.index]
	if source.HasNext() {
		heap.Push(&results.sourceHeap, &queryRowGeneration{
			row:        source.Next(),
			generation: result.generation + 1,
			index:      result.index,
		})
	}
	return result
}

func (results *queryResultsParallel) pushFromSource(index int, generation int) {
	source := results.sources[index]
	if source.HasNext() {
		heap.Push(&results.sourceHeap, &queryRowGeneration{
			row:        source.Next(),
			generation: generation,
			index:      index,
		})
	}
}

func (h queryResultsParallelHeap) Len() int {
	return len(h)
}

func (h queryResultsParallelHeap) Less(i int, j int) bool {
	return h[i].row.Weight() > h[j].row.Weight()
}

func (h queryResultsParallelHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *queryResultsParallelHeap) Push(item interface{}) {
	*h = append(*h, item.(*queryRowGeneration))
}

func (h *queryResultsParallelHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *queryResultsParallelHeap) Next() *queryRowGeneration {
	return heap.Pop(h).(*queryRowGeneration)
}
