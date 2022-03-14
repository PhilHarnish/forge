package query_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
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

	It("returns metadata for regex", func() {
		t := retrie.NewReTrie("(ab)(cd)", 1)
		q := query.Select().From(t)
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM (ReTrie: ABCD ◌◌◌◌●);
				Score | Text.Text | Text.1 | Text.2
				===================================
				1.00  | abcd      | ab     | cd
		`))
	})

	It("returns metadata for tricky regex", func() {
		t := retrie.NewReTrie("a(bxyz)?[a-c]", 1)
		q := query.Select().From(t)
		Expect(q.String(true)).To(matchers.LookLike(`
				SELECT *
				FROM (ReTrie: Abcxyz ◌◌●◌◌◌●);
				Score | Text.Text | Text.1
				==========================
				1.00  | aa        |
				--------------------------
				1.00  | abxyzc    | bxyz
				--------------------------
				1.00  | abxyzb    | bxyz
				--------------------------
				1.00  | abxyza    | bxyz
				--------------------------
				1.00  | ac        |
				--------------------------
				1.00  | ab        |
		`))
	})
})
