package query

import (
	"container/heap"

	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type QueryResultsSource interface {
	Results() QueryResults
	String() string
}

type QueryResults interface {
	HasNext() bool
	Next() QueryResult
}

type QueryResult = *weight.WeightedString

func QueryResultsString(results QueryResults) string {

	return ""
}

type queryResults struct {
	query     *Query
	returned  int
	remaining []queryResults
	heap      queryResultHeap
}

type queryResultHeap []QueryResult

func newQueryResults(query *Query) *queryResults {
	return &queryResults{
		query: query,
	}
}

func (results *queryResults) HasNext() bool {
	return (results.query.limit == 0 || results.returned < results.query.limit) && len(results.getHeap()) > 0
}

func (results *queryResults) Next() QueryResult {
	results.returned++
	return results.heap.Next()
}

func (results *queryResults) getHeap() queryResultHeap {
	if results.heap == nil {
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
