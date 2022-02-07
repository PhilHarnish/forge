package query

type queryResultsNull struct{}

var queryResultsNullSource = &queryResultsNull{}

func (results *queryResultsNull) HasNext() bool {
	return false
}

func (results *queryResultsNull) Next() QueryResult {
	panic("No results")
}
