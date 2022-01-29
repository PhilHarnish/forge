package cursor

import (
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

// Graph node with bloom-filter style optimizations.
type Cursor struct {
	// Accumulated characters.
	Path []byte
	// Current position.
	NodeIterator node.NodeIterator
}

func NewCursor(root node.NodeIterator) *Cursor {
	return &Cursor{
		Path:         []byte{},
		NodeIterator: root,
	}
}

func (cursor *Cursor) String() string {
	return fmt.Sprintf("Cursor('%s', %v)",
		cursor.Path,
		cursor.NodeIterator,
	)
}
