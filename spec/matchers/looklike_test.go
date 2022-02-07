package matchers_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/spec/matchers"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tests")
}

var _ = Describe("LookLike", func() {
	It("Equates two empty strings", func() {
		Expect("").To(matchers.LookLike(""))
	})

	It("Equates two all-whitespace strings", func() {
		Expect("    ").To(matchers.LookLike("\t\t\t"))
	})

	It("Equates indented strings", func() {
		Expect(`
		  Example
		  with
		  indentation
		`).To(matchers.LookLike("Example\nwith\nindentation"))
	})

	It("Notices a sub-indent", func() {
		Expect(`
		  def foo():
		    return 42
		`).To(matchers.LookLike("def foo():\n  return 42"))
	})

	It("Notices when a line begins with text", func() {
		Expect(`this test breaks indentation
		  Example
		  with
		  indentation
		`).NotTo(matchers.LookLike("Example\nwith\nindentation"))
	})

	It("Ignores trailing whitespace in expect", func() {
		Expect(`
			Normal line
			There is whitespace after this:  
			Normal line
		`).To(matchers.LookLike("Normal line\nThere is whitespace after this:\nNormal line"))
	})

	It("Ignores trailing whitespace in LooksLike", func() {
		Expect(`
			Normal line
			There is whitespace after this:
			Normal line
		`).To(matchers.LookLike("Normal line\nThere is whitespace after this:   \nNormal line"))
	})
})
