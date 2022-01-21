package bloom

import (
	"fmt"
	"unsafe"
)

// Graph node with bloom-filter style optimizations.
type Cursor struct {
	// Current position.
	node *Node
	// Accumulated characters.
	path []byte
	// Subpath into the current node
	subpath string
}

func NewCursor(root *Node) *Cursor {
	return &Cursor{
		node:    root,
		path:    []byte{},
		subpath: "",
	}
}

func (cursor *Cursor) Get(path string) (*Cursor, error) {
	for _, c := range path {
		cursor.path = append(cursor.path, string(c)...)
	}
	return cursor, nil
}

func (cursor *Cursor) Has(path string) bool {
	_, err := cursor.Get(path)
	return err == nil
}

func (cursor *Cursor) Select(path string) *Cursor {
	result, err := cursor.Get(path)
	if err != nil {
		panic(fmt.Errorf("path %s not found on %s", path, cursor.node))
	}
	return result
}

func (cursor *Cursor) String() string {
	return fmt.Sprintf("Cursor('%s%s', %s)",
		// Ref strings/builder.go in Go standard library.
		*(*string)(unsafe.Pointer(&cursor.path)),
		cursor.subpath,
		cursor.node,
	)
}
