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
	runes := []rune(path)
	// Preprocess path to determine the requirements along path.
	requirements := make([]BitMask, len(runes))
	required := BitMask(0)
	for i := len(runes) - 1; i >= 0; i-- {
		mask, err := AlphabetMask(runes[i])
		if err != nil {
			return cursor, fmt.Errorf(
				"%s traversal error for '%s': %w", cursor, path, err)
		}
		required |= mask
		requirements[i] = required
	}
	node := cursor.node
	for i, c := range path {
		// Ensure requirements are met at this layer.
		required := requirements[i]
		if node.provideMask&required != required {
			// Eventually one of our requested letters will be missing.
			missing := required ^ cursor.node.provideMask&required
			return cursor, fmt.Errorf(
				"%s traversal error for '%s': '%s' not provided",
				cursor, path, MaskAlphabet(missing, missing))
		}
		position, _ := Position(c)
		// NB: Here we assume `links` is defined, `position` is valid,
		// because the `provide` check has passed.
		link := node.links[position]
		if link == nil {
			return cursor, fmt.Errorf(
				"%s traversal error for '%s': '%c' not linked",
				cursor, path, c)
		}
		if link.prefix != "" {
			return cursor, fmt.Errorf(
				"%s traversal error for '%s': '%s' has unsupported prefix '%s'",
				cursor, path, link.node, link.prefix)
		}
		// Traversal successful, descend into `node` and continue looping.
		node = link.node
		cursor.path = append(cursor.path, string(c)...)
		cursor.node = node
	}
	return cursor, nil
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
