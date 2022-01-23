package query

import (
	"fmt"
	"strings"
)

type Query struct {
	limit int
}

func Select() *Query {
	return &Query{}
}

func (query *Query) Limit(count int) *Query {
	query.limit = count
	return query
}

func (query *Query) Next() *struct{} {
	return nil
}

func (query *Query) String() string {
	lines := []string{
		"SELECT *",
	}
	if query.limit > 0 {
		lines = append(lines, fmt.Sprintf("LIMIT %d", query.limit))
	}
	return strings.Join(lines, "\n")
}
