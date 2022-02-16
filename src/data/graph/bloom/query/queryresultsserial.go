package query

type queryResultsSerial struct {
	query    *Query
	returned int
	results  QueryResults
}

func (results *queryResultsSerial) HasNext() bool {
	return (results.query.limit == 0 || results.returned < results.query.limit) &&
		results.getResults().HasNext()
}

func (results *queryResultsSerial) Next() QueryRow {
	results.returned++
	return results.results.Next()
}

func (results *queryResultsSerial) getResults() QueryResults {
	if results.results == nil {
		results.results = results.query.sources[0].Results()
	}
	return results.results
}

func (results *queryResultsSerial) String() string {
	return resultsString(results.query.Header(), results)
}
