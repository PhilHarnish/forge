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

type queryResults struct {
	rows QueryRows
}

func NewQueryResults(rows QueryRows) QueryResults {
	return &queryResults{
		rows: rows,
	}
}

func (source *queryResults) HasNext() bool {
	return len(source.rows) > 0
}

func (source *queryResults) Next() QueryRow {
	next := source.rows[0]
	source.rows = source.rows[1:]
	return next
}

func newQueryResultsForQuery(query *Query) QueryResults {
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
