package query

import (
	"container/heap"
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type queryResultsParallel struct {
	query    *Query
	returned [][]QueryResult
	sources  queryResultsSources
	heap     queryResultHeap
}

type queuedQueryResult struct {
	index  int
	result QueryResult
}

type queryResultsSources []QueryResults
type queryResultHeap []*queuedQueryResult

func (results *queryResultsParallel) HasNext() bool {
	return (results.query.limit == 0 || len(results.returned) < results.query.limit) &&
		len(results.getHeap()) > 0
}

func (results *queryResultsParallel) Next() QueryResult {
	result := &weight.WeightedStrings{
		Weight:  1.0,
		Strings: make([]string, len(results.query.sources)),
	}
	if len(results.returned) == 0 && len(results.heap) == len(results.sources) {
		// The very first result is pre-determined.
		returned := make([]QueryResult, len(results.sources))
		results.returned = append(results.returned, returned)
		for index, item := range results.heap {
			if len(item.result.Strings) != 1 {
				panic(fmt.Sprintf("Source must return exactly 1 string; given: [%v]",
					item.result.Strings))
			}
			returned[index] = item.result
			result.Weight *= item.result.Weight
			result.Strings[index] = item.result.Strings[0]
		}
		results.heap = results.heap[:0] // Truncate.
		for index, source := range results.sources {
			if source.HasNext() {
				results.heap.Push(&queuedQueryResult{
					index:  index,
					result: source.Next(),
				})
			}
		}
		heap.Init(&results.heap)
		return result
	}
	panic("Not implemented")
}

func (results *queryResultsParallel) getHeap() queryResultHeap {
	if results.sources == nil {
		results.returned = [][]QueryResult{}
		results.sources = make(queryResultsSources, len(results.query.sources))
		results.heap = queryResultHeap{}
		for index, source := range results.query.sources {
			sourceResults := source.Results()
			results.sources[index] = sourceResults
			if !sourceResults.HasNext() {
				// If one of the sources are empty then there are no results overall.
				return results.heap
			}
		}
		for index, sourceResults := range results.sources {
			// Prime the heap after confirming all sources HasNext().
			results.heap = append(results.heap, &queuedQueryResult{
				index:  index,
				result: sourceResults.Next(),
			})
		}
	}
	return results.heap
}

func (h queryResultHeap) Len() int {
	return len(h)
}

func (h queryResultHeap) Less(i int, j int) bool {
	// This should be comparing the
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

func (h *queryResultHeap) Next() queuedQueryResult {
	return heap.Pop(h).(queuedQueryResult)
}
