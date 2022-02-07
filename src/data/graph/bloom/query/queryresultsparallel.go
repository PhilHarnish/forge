package query

import "container/heap"

type queryResultsParallel struct {
	query    *Query
	returned []QueryResult
	heap     queryResultHeap
}

type queryResultHeap []QueryResult

func (results *queryResultsParallel) HasNext() bool {
	return (results.query.limit == 0 || len(results.returned) < results.query.limit) &&
		len(results.getHeap()) > 0
}

func (results *queryResultsParallel) Next() QueryResult {
	panic("Not implemented")
}

func (results *queryResultsParallel) getHeap() queryResultHeap {
	if results.heap == nil {
		results.returned = []QueryResult{}
		results.heap = queryResultHeap{}
		for _, source := range results.query.sources {
			sourceResults := source.Results()
			for sourceResults.HasNext() {
				results.heap = append(results.heap, sourceResults.Next())
			}
		}
	}
	heap.Init(&results.heap)
	return results.heap
}

func (h queryResultHeap) Len() int {
	return len(h)
}

func (h queryResultHeap) Less(i int, j int) bool {
	// This should be comparing the
	return h[i].Weight > h[j].Weight
}

func (h queryResultHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *queryResultHeap) Push(item interface{}) {
	*h = append(*h, item.(QueryResult))
}

func (h *queryResultHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *queryResultHeap) Next() QueryResult {
	return heap.Pop(h).(QueryResult)
}
