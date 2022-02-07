package query

import (
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

type QueryResult = *weight.WeightedStrings

func newQueryResults(query *Query) QueryResults {
	if len(query.sources) == 0 {
		return queryResultsNullSource
	} else if len(query.sources) == 1 {
		return &queryResultsSerial{
			query: query,
		}
	}
	return &queryResultsParallel{
		query: query,
	}
}
