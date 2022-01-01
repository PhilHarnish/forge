package go_euler_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	"testing"
)

func TestGoEuler(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "GoEuler Suite")
}
