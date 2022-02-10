package query

type QueryResultsSource interface {
	Results() QueryResults
	Header() QueryRowHeader
	String() string
}

type QueryResults interface {
	HasNext() bool
	Next() QueryRow
}

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
