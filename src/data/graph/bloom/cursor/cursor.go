package cursor

import (
	"fmt"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

// Graph node with bloom-filter style optimizations.
type Cursor struct {
	// Current position.
	NodeIterator node.NodeIterator
	// Accumulated characters.
	Path []byte
}

func NewCursor(root node.NodeIterator) *Cursor {
	return &Cursor{
		NodeIterator: root,
		Path:         []byte{},
	}
}

func (cursor *Cursor) String() string {
	return fmt.Sprintf("Cursor('%s', %v)",
		cursor.Path,
		cursor.NodeIterator,
	)
}
