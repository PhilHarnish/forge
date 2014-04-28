package go_euler

import (
	"fmt"
	"github.com/onsi/ginkgo"
)

func Problem3(n int) int {
	fmt.Fprintln(ginkgo.GinkgoWriter, "factoring :", n)
	f := Factor(n)
	fmt.Fprintln(ginkgo.GinkgoWriter, "factoring :", f(), f())
	f = Factor(n)
	last, next := 0, f()
	for next != 0 {
		fmt.Fprintln(ginkgo.GinkgoWriter, "next:", last, next)
		last, next = next, f()
		fmt.Fprintln(ginkgo.GinkgoWriter, "next:", last, next)
	}
	return last
}
