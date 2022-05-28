package debug

import "github.com/philharnish/forge/src/data/graph/bloom/node"

type testGenerator struct{}

func NewTestGenerator() *testGenerator {
	return &testGenerator{}
}

func (generator *testGenerator) Items(iterator node.NodeIterator) node.NodeItems {
	return iterator.Items(generator)
}

func (generator *testGenerator) Subscribe(setter node.NodeStateUpdater) {
}
