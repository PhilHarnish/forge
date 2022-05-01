package slices_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"github.com/philharnish/forge/src/data/graph/bloom/mask"
)

var _ = Describe("Default masks", func() {
	It("NONE is matches none of ALPHABET", func() {
		for _, c := range mask.ALPHABET {
			m, _ := mask.AlphabetMask(c)
			Expect(m & mask.NONE).To(Equal(mask.Mask(0)))
		}
	})
})
