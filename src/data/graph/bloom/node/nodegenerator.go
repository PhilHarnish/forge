package node

// NodeGenerators are transient visitors used during Node traversal.
type nodeGenerator struct{}

type NodeGenerator interface {
	Items(iterator NodeIterator) NodeItems
}

var NodeGenerateAll *nodeGenerator = nil

func (generator *nodeGenerator) Items(iterator NodeIterator) NodeItems {
	return iterator.Items(generator)
}
