package main

import "github.com/philharnish/forge/src/data/graph/bloom/benchmarks"

func main() {
	benchmarks.ArraySizes()
	benchmarks.MapSizes()
	// Run C bindings.
	cbindings()
}
