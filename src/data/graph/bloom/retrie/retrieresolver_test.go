package retrie_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	"github.com/philharnish/forge/spec/matchers"
	"github.com/philharnish/forge/src/data/graph/bloom/debug"
	"github.com/philharnish/forge/src/data/graph/bloom/retrie"
)

var _ = Describe("ReTrie resolver", func() {
	BeforeEach(func() {
		retrie.ClearRegistry()
	})

	It("panics when undefined embeddings are requested", func() {
		Expect(func() {
			retrie.NewReTrie("{undefined}", 1.0)
		}).To(PanicWith("Embeded node '$undefined' not found"))
	})

	It("prevents duplicate registrations", func() {
		child := retrie.NewReTrie("", 1.0)
		retrie.Register("a", child)
		Expect(func() {
			retrie.Register("a", child)
		}).To(PanicWith("Cannot register 'a' to ReTrie: 100 ●, ReTrie: 100 ● already registered"))
	})

	It("finds registered nodes", func() {
		child := retrie.NewReTrie("example", 1.0)
		retrie.Register("defined", child)
		parent := retrie.NewReTrie("{defined}", 1.0)
		Expect(debug.StringChildren(parent)).To(matchers.LookLike(`
			((ReTrie: AELMPX) + (ReTrie: 100)): AELMPX
			│◌◌◌◌◌◌◌●
			└example●->ReTrie: 100
		`))
	})
})
