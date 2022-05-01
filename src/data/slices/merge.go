package slices

import (
	"container/heap"
	"sort"
)

type intHeap []int

func MergeInts(a []int, b []int) []int {
	if len(a)+len(b) == 0 {
		return nil
	}
	var heapA intHeap = a
	var heapB intHeap = b
	result := make([]int, 0, len(heapA)+len(heapB))
	aIsSorted := sort.IntsAreSorted(heapA)
	bIsSorted := sort.IntsAreSorted(heapB)
	if !aIsSorted {
		heap.Init(&heapA)
	}
	if !bIsSorted {
		heap.Init(&heapB)
	}
	for len(heapA) > 0 && len(heapB) > 0 {
		nextA := heapA[0]
		nextB := heapB[0]
		if nextA < nextB {
			result = append(result, nextA)
			if aIsSorted {
				heapA = heapA[1:]
			} else {
				heap.Pop(&heapA)
			}
		} else {
			result = append(result, nextB)
			if bIsSorted {
				heapB = heapB[1:]
			} else {
				heap.Pop(&heapB)
			}
		}
	}
	// Only heapA xor heapB still have elements.
	if aIsSorted {
		result = append(result, heapA...)
	} else {
		for len(heapA) > 0 {
			result = append(result, heap.Pop(&heapA).(int))
		}
	}
	if bIsSorted {
		result = append(result, heapB...)
	} else {
		for len(heapB) > 0 {
			result = append(result, heap.Pop(&heapB).(int))
		}
	}
	// Now make values unique.
	last := result[0]
	nextPosition := 1
	cursor := 1
	for cursor < len(result) {
		if result[cursor] == last {
			// Skip.
		} else {
			last = result[cursor]
			result[nextPosition] = last
			nextPosition++
		}
		cursor++
	}
	return result[:nextPosition]
}

func (h intHeap) Len() int {
	return len(h)
}

func (h intHeap) Less(i int, j int) bool {
	return h[i] < h[j]
}

func (h intHeap) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *intHeap) Push(item interface{}) {
	*h = append(*h, item.(int))
}

func (h *intHeap) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}
