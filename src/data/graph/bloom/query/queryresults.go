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
	Next() *weight.WeightedStringsSet
}

type queryResults struct {
	query *Query
	heap  queryResultHeap
}

type queryResultHeap []*weight.WeightedStringsSet

func newQueryResults(query *Query) *queryResults {
	return &queryResults{
		query: query,
	}
}

func (results *queryResults) HasNext() bool {
	return len(results.getHeap()) > 0
}

func (results *queryResults) Next() *weight.WeightedStringsSet {
	return results.heap.Pop().(*weight.WeightedStringsSet)
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
	index := 0
	iResults := *h[i]
	jResults := *h[j]
	iLen := len(iResults)
	jLen := len(jResults)
	maxIndex := iLen - 1
	if jLen < iLen {
		maxIndex = jLen - 1
	}
	for index < maxIndex {
		if iResults[index].Weight > jResults[index].Weight {
			return true
		}
		index++
	}
	// NB: "Less" is inverted to implement a max-heap.
	return iResults[index].Weight > jResults[index].Weight
}

func (h queryResultHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *queryResultHeap) Push(item interface{}) {
	*h = append(*h, item.(*weight.WeightedStringsSet))
}

func (h *queryResultHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *queryResultHeap) Next() *weight.WeightedStringsSet {
	return heap.Pop(h).(*weight.WeightedStringsSet)
}
