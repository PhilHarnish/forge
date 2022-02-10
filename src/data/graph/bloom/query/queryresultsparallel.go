package query

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

func (results *queryResultsParallel) HasNext() bool {
	return false
}

func (results *queryResultsParallel) Next() QueryRow {
	return nil
}
