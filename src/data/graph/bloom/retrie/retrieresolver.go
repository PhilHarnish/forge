package retrie

import (
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

var embeddedNodeRegistry = initRegistry()

func initRegistry() map[string]node.NodeIterator {
	return map[string]node.NodeIterator{}
}

func ClearRegistry() {
	embeddedNodeRegistry = initRegistry()
}

func Register(id string, embeddedNode node.NodeIterator) {
	if item, exists := embeddedNodeRegistry[id]; exists {
		panic(fmt.Sprintf("Cannot register '%s' to %s, %s already registered",
			id, item.String(), embeddedNode.String()))
	}
	embeddedNodeRegistry[id] = embeddedNode
}

func resolve(id string) node.NodeIterator {
	if id[0] == '$' {
		id = id[1:]
		if item, exists := embeddedNodeRegistry[id]; exists {
			return item
		}
	}
	return nil
}
