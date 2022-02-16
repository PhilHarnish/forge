package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

var _ = Describe("Results", func() {
	It("Returns no results for empty Trie", func() {
		q := query.Select().From(trie.NewTrie())
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM Trie('', '', 0);
				∅
		`))
	})

	It("Returns result for shallow Trie", func() {
		t := trie.NewTrie()
		t.Add("child", 1.0)
		q := query.Select().From(t)
		Expect(q.String()).To(matchers.LookLike(`
				SELECT *
				FROM Trie('CDHIL', '     #', 0);
				Score | Text
				=============
				1.00  | child
		`))
	})
})
