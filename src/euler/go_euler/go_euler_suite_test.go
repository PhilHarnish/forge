package go_euler_test

import (
  . "github.com/onsi/ginkgo"
  . "github.com/onsi/gomega"

  "testing"
)

func TestGoEuler(t *testing.T) {
  RegisterFailHandler(Fail)
  RunSpecs(t, "GoEuler Suite")
}
