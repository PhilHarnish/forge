package go_euler

import (
	"container/heap"
	"sync"
)

// An CompositeHeap is a min-heap of (pos, prime) tuples.
// See: http://golang.org/pkg/container/heap/.
type Composite struct {
	Pos   int
	Prime int
}

type CompositeHeap []*Composite

func (h CompositeHeap) Len() int           { return len(h) }
func (h CompositeHeap) Less(i, j int) bool { return h[i].Pos < h[j].Pos }
func (h CompositeHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *CompositeHeap) Push(x interface{}) {
	// Push and Pop use pointer receivers because they modify the slice's length,
	// not just its contents.
	*h = append(*h, x.(*Composite))
}

func (h *CompositeHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

var compositeHeap *CompositeHeap = &CompositeHeap{
	// Not needed because even numbers are skipped:
	// &Composite{4, 2},
	&Composite{9, 3},
}

var knownPrimes []int = []int{2, 3}
var primesRwLock sync.RWMutex
var generateLock sync.Mutex

/**
 * Generating primes with sieve.
 * See: http://www.cs.hmc.edu/~oneill/papers/Sieve-JFP.pdf
 *
 * This approach is slightly slower than trial division. Before identifying the
 * memory bottleneck it was significantly slower.
 *
 * primesSieve(2000000) was substantially slower than calling the function in
 * small steps and progressively reaching 2000000 (2 minutes vs 7 seconds).
 *
 * Attempted optimizations:
 * 1) Skipping even numbers. Paper suggests 77% improvement. Observed: ~20%.
 * 2) Generating target primes directly. Substantially slower than calling the
 *    function in small steps and progressively reaching 2000000.
 *    (2 minutes vs 7 seconds.) This mystery applies to trial division as well
 *    and appears to be platform specific (Mac OSX only). Attempts to profile
 *    have failed. See related:
 *    http://godoc.org/code.google.com/p/rsc/cmd/pprof_mac_fix
 * 3) Allocating a full block of memory in advance, rather than append doubling.
 *    No real difference in performance. Removed. Unclear if there is a way to
 *    pre-allocate and use from that pool without tons of hacks.
 *
 * Ultimately the performance problem was from allocating lots of objects:
 *   min := (*compositeHeap)[0]  // New object.
 *   // ...
 *   heap.Push(compositeHeap, min)  // Escapes local scope. Expensive.
 */
func GetPrime(ceil int) int {
	if ceil < len(knownPrimes) {
		return knownPrimes[ceil]
	}
	generateLock.Lock()
	defer generateLock.Unlock()

	min := (*compositeHeap)[0]
	// No lock needed; knownPrimes is append only and GC won't remove value until
	// we release pointer.
	largestPrime := knownPrimes[len(knownPrimes)-1]
	for i := largestPrime + 2; len(knownPrimes) <= ceil; i += 2 {
		for i > min.Pos {
			// Increase the multiple and fix the entry.
			min.Pos += min.Prime
			heap.Fix(compositeHeap, 0)
			// Look at the new lowest composite.
			min = (*compositeHeap)[0]
		}
		if i < min.Pos {
			// Eg: i == 3, i < 4. Insert new prime 3 as {3*3, 3}.
			// When another prime (eg, 7) is discovered, do the same.
			primesRwLock.Lock()
			knownPrimes = append(knownPrimes, i)
			primesRwLock.Unlock()
			heap.Push(compositeHeap, &Composite{i * i, i})
		}
	}
	return knownPrimes[ceil]
}
