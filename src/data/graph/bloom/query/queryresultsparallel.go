package query

import (
	"container/heap"
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type queryResultsParallel struct {
	query       *Query
	resultQueue [][]QueryResult
	cursor      int
	sources     queryResultsSources
	heap        queryResultHeap
}

type queuedQueryResult struct {
	index  int
	result QueryResult
}

type queryResultsSources []QueryResults
type queryResultHeap []*queuedQueryResult

func (results *queryResultsParallel) HasNext() bool {
	// Warning: results.getHeap() feeds results.resultQueue.
	return results.withinLimit(results.cursor) &&
		(results.canGenerateMore() || results.hasGeneratedResults())
}

func (results *queryResultsParallel) Next() QueryResult {
	if !results.hasGeneratedResults() && results.canGenerateMore() {
		nextItem := results.heap.Next()
		results.pushFromSource(nextItem.index)
		for _, previousResult := range results.resultQueue {
			nextResult := make([]QueryResult, len(results.query.sources))
			results.resultQueue = append(results.resultQueue, nextResult)
			copy(nextResult, previousResult)
			nextResult[nextItem.index] = nextItem.result
			if !results.withinLimit(len(results.resultQueue)) {
				break
			}
		}
	}
	queuedResult := results.resultQueue[results.cursor]
	results.cursor++
	result := &weight.WeightedStrings{
		Weight:  1.0,
		Strings: make([]string, len(results.query.sources)),
	}
	for index, item := range queuedResult {
		if len(item.Strings) != 1 {
			panic(fmt.Sprintf("TODO: Source must return exactly 1 string; given: [%v]",
				item.Strings))
		}
		result.Weight *= (*item).Weight
		result.Strings[index] = item.Strings[0]
	}
	return result
}

func (results *queryResultsParallel) withinLimit(i int) bool {
	return results.query.limit == 0 || i <= results.query.limit
}

func (results *queryResultsParallel) canGenerateMore() bool {
	return len(results.getHeap()) > 0
}

func (results *queryResultsParallel) hasGeneratedResults() bool {
	results.getHeap() // May add items to results.resultQueue.
	return results.cursor < len(results.resultQueue)
}

func (results *queryResultsParallel) getHeap() queryResultHeap {
	if results.heap == nil && results.sources == nil {
		results.sources = make(queryResultsSources, len(results.query.sources))
		for index, source := range results.query.sources {
			sourceResults := source.Results()
			results.sources[index] = sourceResults
			if !sourceResults.HasNext() {
				// If one of the sources are empty then there are no results overall.
				return results.heap
			}
		}
		// The first result is pre-determined.
		nextResult := make([]QueryResult, len(results.query.sources))
		results.resultQueue = [][]QueryResult{nextResult}
		// Also, prime the heap with the next result (if possible).
		results.heap = queryResultHeap{}
		for index, source := range results.sources {
			nextResult[index] = source.Next()
			results.pushFromSource(index)
		}
		heap.Init(&results.heap)
	}
	return results.heap
}

func (results *queryResultsParallel) pushFromSource(index int) {
	source := results.sources[index]
	if source.HasNext() {
		heap.Push(&results.heap, &queuedQueryResult{
			index:  index,
			result: source.Next(),
		})
	}
}

func (h queryResultHeap) Len() int {
	return len(h)
}

func (h queryResultHeap) Less(i int, j int) bool {
	return h[i].result.Weight > h[j].result.Weight
}

func (h queryResultHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *queryResultHeap) Push(item interface{}) {
	*h = append(*h, item.(*queuedQueryResult))
}

func (h *queryResultHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *queryResultHeap) Next() *queuedQueryResult {
	return heap.Pop(h).(*queuedQueryResult)
}
