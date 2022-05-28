package debug

import "github.com/philharnish/forge/src/data/graph/bloom/node"

type TestGenerator struct {
	Subscribers []node.NodeStateUpdater
}

func NewTestGenerator() *TestGenerator {
	return &TestGenerator{}
}

func (generator *TestGenerator) Items(iterator node.NodeIterator) node.NodeItems {
	return iterator.Items(generator)
}

func (generator *TestGenerator) Subscribe(setter node.NodeStateUpdater) {
	generator.Subscribers = append(generator.Subscribers, setter)
}
