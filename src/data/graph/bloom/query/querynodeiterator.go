package query

import (
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type queryNodeResultsSource struct {
	iterator node.NodeIterator
}

type queryNodeResults struct {
}

func queryNodeIterator(iterator node.NodeIterator) QueryResultsSource {
	return &queryNodeResultsSource{iterator: iterator}
}

func (source *queryNodeResultsSource) Results() QueryResults {
	return &queryNodeResults{}
}

func (source *queryNodeResultsSource) String() string {
	return source.iterator.String()
}

func (results *queryNodeResults) HasNext() bool {
	return false
}

func (results *queryNodeResults) Next() QueryResult {
	return nil
}
