package query

import (
	"fmt"
	"strings"
)

type Query struct {
	limit        int
	namedSources map[string]QuerySource
	sources      []*querySource
	iterator     func() *QueryResult
}

type querySource struct {
	name   string
	source QuerySource
}

type QuerySource interface {
	Next() *QueryResult
	String() string
}

type QueryResult = struct{}

func Select() *Query {
	return &Query{
		namedSources: map[string]QuerySource{},
	}
}

func (query *Query) As(name string) *Query {
	if len(query.sources) == 0 {
		panic("no sources available")
	}
	lastSource := query.sources[len(query.sources)-1]
	if lastSource.name != "" {
		panic(fmt.Sprintf(
			"cannot name source %s '%s', already assigned name '%s'",
			lastSource.source.String(), name, lastSource.name))
	}
	lastSource.name = name
	query.namedSources[name] = lastSource.source
	return query
}

func (query *Query) From(sources ...QuerySource) *Query {
	for _, source := range sources {
		query.sources = append(query.sources, &querySource{source: source})
	}
	return query
}

func (query *Query) Limit(count int) *Query {
	query.limit = count
	return query
}

func (query *Query) Next() *QueryResult {
	if query.iterator == nil {
		query.iterator = func() *QueryResult {
			for _, source := range query.sources {
				result := source.source.Next()
				if result != nil {
					return result
				}
			}
			return nil
		}
	}

	return query.iterator()
}

func (query *Query) String() string {
	lines := []string{
		"SELECT *",
	}
	if len(query.sources) == 1 && len(query.namedSources) == 0 {
		// Special case for one unnamed source.
		lines = append(lines,
			fmt.Sprintf("FROM %s", query.sources[0].source.String()))
	} else if len(query.namedSources)+len(query.sources) > 0 {
		sources := []string{}
		for _, source := range query.sources {
			if source.name == "" {
				sources = append(sources, fmt.Sprintf("\t%s", source.source.String()))
			} else {
				sources = append(sources, fmt.Sprintf("\t%s AS %s", source.source.String(), source.name))
			}
		}
		lines = append(lines, "FROM")
		lines = append(lines, strings.Join(sources, ",\n"))
	}
	if query.limit > 0 {
		lines = append(lines, fmt.Sprintf("LIMIT %d", query.limit))
	}
	return strings.Join(lines, "\n")
}
