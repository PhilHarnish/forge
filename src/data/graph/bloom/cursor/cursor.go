package cursor

import (
	"fmt"
	"strings"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

// Graph node with bloom-filter style optimizations.
type Cursor struct {
	// Current position.
	Node *node.Node
	// Accumulated characters.
	Path []byte
}

func NewCursor(root *node.Node) *Cursor {
	return &Cursor{
		Node: root,
		Path: []byte{},
	}
}

func (cursor *Cursor) Get(path string) (*Cursor, error) {
	runes := []rune(path)
	// Preprocess path to determine the requirements along path.
	requirements := make([]mask.Mask, len(runes))
	required := mask.Mask(0)
	for i := len(runes) - 1; i >= 0; i-- {
		mask, err := mask.AlphabetMask(runes[i])
		if err != nil {
			return cursor, fmt.Errorf(
				"%s traversal error for '%s': %w", cursor, path, err)
		}
		required |= mask
		requirements[i] = required
	}
	cursorNode := cursor.Node
	for i := 0; i < len(runes); i++ {
		c := runes[i]
		// Ensure requirements are met at this layer.
		required := requirements[i]
		if cursorNode.ProvideMask&required != required {
			// Eventually one of our requested letters will be missing.
			missing := required ^ cursor.Node.ProvideMask&required
			return cursor, fmt.Errorf(
				"%s traversal error for '%s': '%s' not provided",
				cursor, path, mask.MaskAlphabet(missing, missing))
		}
		position := 0
		for ; position < len(cursorNode.Links); position++ {
			if strings.HasPrefix(cursorNode.Links[position].Prefix, string(c)) {
				break
			}
		}
		if position == len(cursorNode.Links) {
			return cursor, fmt.Errorf(
				"%s traversal error for '%s': '%c' not linked",
				cursor, path, c)
		}
		link := cursorNode.Links[position]
		prefixStart := i
		// NB: Start Prefix scan from 1; 0 checked above.
		for _, p := range link.Prefix[1:] {
			i++
			if i >= len(runes) {
				return cursor, fmt.Errorf(
					"%s traversal error for '%s': exhausted input traversing prefix '%s' on %s[%c]",
					cursor, path, link.Prefix, cursorNode, c)
			} else if p != runes[i] {
				return cursor, fmt.Errorf(
					"%s traversal error for '%s': prefix mismatch '%c%s' is not a prefix of '%s'",
					cursor, path, c, link.Prefix[1:], path[prefixStart:])
			}
		}
		// Traversal successful, descend into `node` and continue looping.
		cursorNode = link.Node
		cursor.Path = append(cursor.Path, []byte(link.Prefix)...)
		cursor.Node = cursorNode
	}
	return cursor, nil
}

func (cursor *Cursor) Select(path string) *Cursor {
	result, err := cursor.Get(path)
	if err != nil {
		panic(fmt.Errorf("path %s not found on %s", path, cursor.Node))
	}
	return result
}

func (cursor *Cursor) String() string {
	return fmt.Sprintf("Cursor('%s', %s)",
		// Ref strings/builder.go in Go standard library.
		cursor.Path,
		cursor.Node,
	)
}
