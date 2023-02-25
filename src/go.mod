module github.com/philharnish/forge/src

go 1.17

require (
	github.com/onsi/ginkgo/v2 v2.0.0
	github.com/onsi/gomega v1.18.0
)

require (
	golang.org/x/net v0.7.0 // indirect
	golang.org/x/sys v0.5.0 // indirect
	golang.org/x/text v0.7.0 // indirect
	gopkg.in/yaml.v2 v2.4.0 // indirect
)

require github.com/philharnish/forge/spec v0.0.0

replace github.com/philharnish/forge/spec v0.0.0 => ../spec
