package benchmarks

import (
	"fmt"
	"runtime"
	"unsafe"
)

// From: https://stackoverflow.com/questions/15313105/memory-overhead-of-maps-in-go
func arraySize(arrays []*[]byte) uint64 {
	var stats runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&stats)
	return stats.Alloc - uint64(unsafe.Sizeof(arrays[0]))*uint64(cap(arrays))
}

func fixedArraySize(arrays []*[64]byte) uint64 {
	var stats runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&stats)
	return stats.Alloc - uint64(unsafe.Sizeof(arrays[0]))*uint64(cap(arrays))
}

func mapSize(maps []*map[rune]byte) uint64 {
	var stats runtime.MemStats
	runtime.GC()
	runtime.ReadMemStats(&stats)
	return stats.Alloc - uint64(unsafe.Sizeof(maps[0]))*uint64(cap(maps))
}

const TESTS = 1000

func ArraySizes() {
	arrays := []*[]byte{}
	n := TESTS
	// Zero size.
	before := arraySize(arrays)
	for i := 0; i < n; i++ {
		a := []byte{}
		arrays = append(arrays, &a)
	}
	after := arraySize(arrays)
	emptyPerArray := float64(after-before) / float64(n)
	fmt.Printf("Bytes used for %d empty arrays: %d, bytes/array %.1f\n", n, after-before, emptyPerArray)
	arrays = nil

	// Variable size.
	k := 1
	for p := 1; p < 8; p++ {
		before = arraySize(arrays)
		for i := 0; i < n; i++ {
			a := []byte{}
			for j := 0; j < k; j++ {
				a = append(a, byte(j))
			}
			arrays = append(arrays, &a)
		}
		after = arraySize(arrays)
		fullPerMap := float64(after-before) / float64(n)
		fmt.Printf("Bytes used for %d arrays with %d entries: %d, bytes/array %.1f\n", n, k, after-before, fullPerMap)
		fmt.Printf("Bytes per entry %.1f\n", (fullPerMap-emptyPerArray)/float64(k))
		k *= 2
	}
	// Fixed size.
	fixed_arrays := []*[64]byte{}
	before = fixedArraySize(fixed_arrays)
	for i := 0; i < n; i++ {
		fixed_array := [64]byte{}
		for j := 0; j < 64; j++ {
			fixed_array[j] = byte(j)
		}
		fixed_arrays = append(fixed_arrays, &fixed_array)
	}
	after = fixedArraySize(fixed_arrays)
	fullPerMap := float64(after-before) / float64(n)
	fmt.Printf("Bytes used for %d arrays with 64 FIXED entries: %d, bytes/map %.1f\n", n, after-before, fullPerMap)
	fmt.Printf("Bytes per entry %.1f\n", (fullPerMap-emptyPerArray)/float64(k))
}

func MapSizes() {
	maps := []*map[rune]byte{}
	n := TESTS
	before := mapSize(maps)
	for i := 0; i < n; i++ {
		h := map[rune]byte{}
		maps = append(maps, &h)
	}
	after := mapSize(maps)
	emptyPerMap := float64(after-before) / float64(n)
	fmt.Printf("Bytes used for %d empty maps: %d, bytes/map %.1f\n", n, after-before, emptyPerMap)
	maps = nil

	k := 1
	for p := 1; p < 8; p++ {
		before = mapSize(maps)
		for i := 0; i < n; i++ {
			h := make(map[rune]byte, k)
			for j := 0; j < k; j++ {
				h[rune(j)] = byte(j)
			}
			maps = append(maps, &h)
		}
		after = mapSize(maps)
		fullPerMap := float64(after-before) / float64(n)
		fmt.Printf("Bytes used for %d maps with %d entries: %d, bytes/map %.1f\n", n, k, after-before, fullPerMap)
		fmt.Printf("Bytes per entry %.1f\n", (fullPerMap-emptyPerMap)/float64(k))
		k *= 2
	}
}
