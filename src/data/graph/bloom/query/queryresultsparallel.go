package query

import (
	"container/heap"
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

// TODO: Compare the performance of...
// 1. Store the results returned from each stream and prepare cross-product on demand.
// 2. Store the final results returned overall and iterate those directly.

type queryResultsParallel struct {
	query *Query
	// returnedResults []*returnedResult
	// queuedResults   queuedResultHeap
	// sources         querySources
	// heap            querySourceHeap
}

type returnedResult struct {
	generation int
	weight     weight.Weight
	results    []QueryRow
}

type queuedSourceResult struct {
	generation int
	index      int
	result     QueryRow
}

type querySources []QueryResults
type querySourceHeap []*queuedSourceResult
type queuedResultHeap []QueryRow

func (results *queryResultsParallel) HasNext() bool {
	return false
	// Warning: results.getHeap() feeds results.resultQueue.
	return results.withinLimit(len(results.returnedResults)) &&
		(results.canGenerateMore() || results.hasGeneratedResults())
}

func (results *queryResultsParallel) Next() QueryRow {
	return nil
	if !results.hasGeneratedResults() && results.canGenerateMore() {
		nextItem := results.takeNextFromSource()
		if finalResultCache {
			for _, previousResult := range results.returnedResults {
				// Undo inclusion of the previous weight...
				newWeight := previousResult.weight / previousResult.results[nextItem.index].Weight
				// ...then include the nextItem's weight
				newWeight *= nextItem.result.Weight
				nextResult := &returnedResult{
					generation: nextItem.generation,
					weight:     previousResult.weight,
					results:    make([]QueryRow, len(previousResult.results)),
				}
				results.returnedResults = append(results.returnedResults, nextResult)
				copy(nextResult.results, previousResult.results)
				nextResult.results[nextItem.index] = nextItem.result
				results.queuedResults.Push(computeQueuedResult(nextResult.results))
			}
		}
		if debugOutput {
			results.returnedResults[len(results.returnedResults)-1].results[nextItem.index].Strings[0] += fmt.Sprintf("-%d", nextItem.generation)
		}
	}
	bestResult := results.queuedResults.Next() // GAH! this needs to be appended to the returned results list?
	return computeQueuedResult(queuedResult.results)
}

func (results *queryResultsParallel) withinLimit(i int) bool {
	return results.query.limit == 0 || i <= results.query.limit
}

func (results *queryResultsParallel) canGenerateMore() bool {
	return len(results.getHeap()) > 0
}

func (results *queryResultsParallel) hasGeneratedResults() bool {
	results.getHeap() // May add items to results.queuedResults.
	return len(results.queuedResults) > 0
}

func (results *queryResultsParallel) getHeap() querySourceHeap {
	if results.heap == nil && results.sources == nil {
		results.sources = make(querySources, len(results.query.sources))
		for index, source := range results.query.sources {
			sourceResults := source.Results()
			results.sources[index] = sourceResults
			if !sourceResults.HasNext() {
				// If one of the sources are empty then there are no results overall.
				return results.heap
			}
		}
		// The first result is pre-determined.
		nextResultSet := make([]QueryRow, len(results.query.sources))
		results.returnedResults = []*returnedResult{}
		// 	{
		// 		results: nextResult,
		// 	},
		// }
		// Also, prime the heap with the next result (if possible).
		results.heap = querySourceHeap{}
		for index, source := range results.sources {
			nextResultSet[index] = source.Next()
			results.pushFromSource(index, 0)
		}
		results.queuedResults = []QueryRow{computeQueuedResult(nextResultSet)}
		heap.Init(&results.heap)
	}
	return results.heap
}

func computeQueuedResult(resultSet []QueryRow) QueryRow {
	computed := &weight.WeightedStrings{
		Weight:  1.0,
		Strings: make([]string, len(resultSet)),
	}
	for index, inputResult := range resultSet {
		if len(inputResult.Strings) != 1 {
			panic(fmt.Sprintf("TODO: Source must return exactly 1 string; given: [%v]",
				inputResult.Strings))
		}
		computed.Weight *= inputResult.Weight
		computed.Strings[index] = inputResult.Strings[0]
	}
	return computed
}

func (results *queryResultsParallel) pushFromSource(index int, generation int) {
	source := results.sources[index]
	if source.HasNext() {
		heap.Push(&results.heap, &queuedSourceResult{
			generation: generation,
			index:      index,
			result:     source.Next(),
		})
	}
}

func (results *queryResultsParallel) takeNextFromSource() *queuedSourceResult {
	nextItem := results.heap.Next()
	nextGeneration := nextItem.generation + 1
	results.pushFromSource(nextItem.index, nextGeneration)
	return nextItem
}

func (h querySourceHeap) Len() int {
	return len(h)
}

func (h querySourceHeap) Less(i int, j int) bool {
	return h[i].result.Weight() > h[j].result.Weight()
}

func (h querySourceHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *querySourceHeap) Push(item interface{}) {
	*h = append(*h, item.(*queuedSourceResult))
}

func (h *querySourceHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *querySourceHeap) Next() *queuedSourceResult {
	return heap.Pop(h).(*queuedSourceResult)
}

func (h queuedResultHeap) Len() int {
	return len(h)
}

func (h queuedResultHeap) Less(i int, j int) bool {
	return h[i].Weight() > h[j].Weight()
}

func (h queuedResultHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *queuedResultHeap) Push(item interface{}) {
	*h = append(*h, item.(QueryRow))
}

func (h *queuedResultHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *queuedResultHeap) Next() QueryRow {
	return heap.Pop(h).(QueryRow)
}
