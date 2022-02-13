package query

import (
	"fmt"
	"strings"

	"github.com/onsi/gomega/gmeasure/table"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

const QUERY_MAX_ROWS = 1000

type Query struct {
	limit        int
	namedSources map[string]int
	sourceNames  map[int]string
	sources      []QueryResultsSource
	header       *queryRowHeader
}

func Select() *Query {
	return &Query{
		namedSources: map[string]int{},
		sourceNames:  map[int]string{},
	}
}

func (query *Query) As(name string) *Query {
	position := len(query.sources) - 1
	if position < 0 {
		panic("no sources available")
	}
	existingName, exists := query.sourceNames[position]
	lastSource := query.sources[position]
	if exists {
		panic(fmt.Sprintf(
			"cannot name source %s '%s', already assigned name '%s'",
			lastSource.String(), name, existingName))
	}
	query.namedSources[name] = position
	query.sourceNames[position] = name
	return query
}

func (query *Query) From(sources ...interface{}) *Query {
	for _, source := range sources {
		var sourceAsQuerySource QueryResultsSource
		switch x := source.(type) {
		case QueryResultsSource:
			sourceAsQuerySource = x
		case node.NodeIterator:
			sourceAsQuerySource = queryNodeIterator(x)
		}
		if sourceAsQuerySource != nil {
			query.sources = append(query.sources, sourceAsQuerySource)
		} else {
			panic(fmt.Sprintf("Source is invalid type: %v", source))
		}
	}
	return query
}

func (query *Query) Limit(count int) *Query {
	query.limit = count
	return query
}

func (query *Query) Results() QueryResults {
	return newQueryResults(query)
}

func (query *Query) String() string {
	lines := []string{
		"SELECT *",
	}
	if len(query.sources) == 1 && len(query.namedSources) == 0 {
		// Special case for one unnamed source.
		lines = append(lines,
			fmt.Sprintf("FROM %s", query.sources[0].String()))
	} else if len(query.sources) == 1 && len(query.namedSources) == 1 {
		// Special case for one named source.
		alias := query.sourceNames[0]
		lines = append(lines,
			fmt.Sprintf("FROM %s AS %s", query.sources[0].String(), alias))
	} else if len(query.namedSources)+len(query.sources) > 0 {
		sources := []string{}
		for position, source := range query.sources {
			alias, exists := query.sourceNames[position]
			if exists {
				sources = append(sources, fmt.Sprintf("\t%s AS %s", source.String(), alias))
			} else {
				sources = append(sources, fmt.Sprintf("\t%s", source.String()))
			}
		}
		lines = append(lines, "FROM")
		lines = append(lines, strings.Join(sources, ",\n"))
	}
	if query.limit > 0 {
		lines = append(lines, fmt.Sprintf("LIMIT %d", query.limit))
	}
	lines[len(lines)-1] = lines[len(lines)-1] + ";"
	results := query.Results()
	if !results.HasNext() {
		lines = append(lines, "∅")
	} else {
		resultsTable := table.NewTable()
		tableRow := table.R(table.Divider("="))
		resultsTable.AppendRow(tableRow)
		tableRow.AppendCell(table.C("Score"))
		for _, label := range query.Header().Labels() {
			tableRow.AppendCell(table.C(label))
		}
		i := 0
		for results.HasNext() {
			i++
			tableRow = table.R()
			if (query.limit != 0 && i > query.limit) || i > QUERY_MAX_ROWS {
				break
			}
			resultsTable.AppendRow(tableRow)
			resultRow := results.Next()
			tableRow.AppendCell(table.C(fmt.Sprintf("%.2f", resultRow.Weight())))
			for _, result := range resultRow.Cells() {
				tableRow.AppendCell(table.C(result.String))
			}
		}
		lines = append(lines, resultsTable.Render())
	}
	return strings.Join(lines, "\n")
}

func (query *Query) Header() QueryRowHeader {
	if query.header == nil {
		query.header = newQueryRowHeaderForQuery(query)
	}
	return query.header
}
