package query

import (
	"fmt"
	"strings"

	"github.com/onsi/gomega/gmeasure/table"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type Query struct {
	limit        int
	namedSources map[string]int
	sourceNames  map[int]string
	sources      []QueryResultsSource
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
		query.sources = append(query.sources, sourceAsQuerySource)
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
		row := table.R(table.Divider("="))
		resultsTable.AppendRow(row)
		row.AppendCell(table.C("Score"))
		for position, source := range query.sources {
			namedPosition, exists := query.sourceNames[position]
			if exists {
				row.AppendCell(table.C(namedPosition))
			} else {
				row.AppendCell(table.C(source.String()))
			}
		}
		for results.HasNext() {
			row = table.R()
			resultsTable.AppendRow(row)
			resultRow := results.Next()
			row.AppendCell(table.C(fmt.Sprintf("%.2f", resultRow.Weight)))
			for _, result := range resultRow.Strings {
				row.AppendCell(table.C(result))
			}
		}
		lines = append(lines, resultsTable.Render())
	}
	return strings.Join(lines, "\n")
}
