package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

var _ = Describe("Results", func() {
	It("Returns no results for empty node", func() {
		q := query.Select().From(trie.NewTrie())
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM Trie('', '', 0);
				∅
		`))
	})
})
