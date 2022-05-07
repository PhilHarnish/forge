package query

import (
	"fmt"
	"strings"

	"github.com/onsi/gomega/gmeasure/table"
)

type QueryResultsSource interface {
	QueryHeaderProvider
	Results() QueryResults
	String(includeResults ...bool) string
}

type QueryHeaderProvider interface {
	Header() QueryRowHeader
}

type QueryResults interface {
	HasNext() bool
	Next() QueryRow
	String() string
}

type queryResults struct {
	header QueryRowHeader
	rows   QueryRows
}

func NewQueryResults(header QueryRowHeader, rows QueryRows) QueryResults {
	return &queryResults{
		header: header,
		rows:   rows,
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

func (source *queryResults) String() string {
	return resultsString(source.header, source)
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

func resultsString(header QueryRowHeader, results QueryResults) string {
	lines := []string{}
	if !results.HasNext() {
		lines = append(lines, "∅")
	} else {
		resultsTable := table.NewTable()
		tableRow := table.R(table.Divider("="))
		resultsTable.AppendRow(tableRow)
		tableRow.AppendCell(table.C("Score"))
		for _, label := range header.Labels() {
			tableRow.AppendCell(table.C(label))
		}
		i := 0
		for results.HasNext() {
			i++
			tableRow = table.R()
			resultsTable.AppendRow(tableRow)
			resultRow := results.Next()
			tableRow.AppendCell(table.C(fmt.Sprintf("%.2f", resultRow.Weight())))
			for _, result := range resultRow.Cells() {
				if result == nil {
					tableRow.AppendCell(table.C("∅"))
				} else {
					tableRow.AppendCell(table.C(result.String))
				}
			}
		}
		lines = append(lines, resultsTable.Render())
	}
	return strings.Join(lines, "\n")
}
