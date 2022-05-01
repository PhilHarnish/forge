package slices_test

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/slices"
)

func Test(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Mask tests")
}

var _ = Describe("MergeInts", func() {
	It("is a no-op for empty inputs", func() {
		Expect(slices.MergeInts(nil, nil)).To(HaveLen(0))
	})

	It("returns combined unique sorted lists", func() {
		Expect(slices.MergeInts([]int{1, 2}, []int{3, 4})).To(Equal([]int{1, 2, 3, 4}))
	})

	It("returns combined unique unsorted lists", func() {
		Expect(slices.MergeInts([]int{2, 1}, []int{4, 3})).To(Equal([]int{1, 2, 3, 4}))
	})

	It("returns combined unique unsorted blended lists", func() {
		Expect(slices.MergeInts([]int{4, 1}, []int{2, 3})).To(Equal([]int{1, 2, 3, 4}))
	})

	It("returns combined unsorted blended lists with duplicates", func() {
		Expect(slices.MergeInts([]int{4, 1, 2}, []int{2, 3, 4})).To(Equal([]int{1, 2, 3, 4}))
		Expect(slices.MergeInts([]int{2, 3, 4}, []int{4, 1, 2})).To(Equal([]int{1, 2, 3, 4}))
	})
})
