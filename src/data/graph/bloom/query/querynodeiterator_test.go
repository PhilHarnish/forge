package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/trie"
)

var _ = Describe("Results", func() {
	It("returns no results for empty Trie", func() {
		q := query.Select().From(trie.NewTrie())
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM (Trie);
				∅
		`))
	})

	It("returns result for shallow Trie", func() {
		t := trie.NewTrie()
		t.Add("child", 1.0)
		q := query.Select().From(t)
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM (Trie: CDHIL ◌◌◌◌◌●);
				Score | Text
				=============
				1.00  | child
		`))
	})

	It("returns result for Trie with children", func() {
		t := trie.NewTrie()
		t.Add("a", .5)
		t.Get("a").Add("c", .25)
		t.Get("a").Add("b", 1.0)
		q := query.Select().From(t)
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM (Trie: A ◌●);
				Score | Text
				============
				1.00  | ab
				------------
				0.50  | a
				------------
				0.25  | ac
		`))
	})
})
