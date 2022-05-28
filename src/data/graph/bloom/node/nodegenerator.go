package node

// NodeGenerators are transient visitors used during Node traversal.
type nodeGenerator struct{}

type NodeGenerator interface {
	Items(iterator NodeIterator) NodeItems
	Subscribe(setter NodeStateUpdater)
}

var NodeGenerateAll *nodeGenerator = nil

func (generator *nodeGenerator) Items(iterator NodeIterator) NodeItems {
	return iterator.Items(generator)
}

func (generator *nodeGenerator) Subscribe(setter NodeStateUpdater) {
}
