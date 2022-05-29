package retrie

import (
	"fmt"
	"regexp/syntax"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type dfaId = uint64

const NO_ID = dfaId(0)

type reTrieDirectory struct {
	table map[dfaId]*reTrieNode
	next  dfaId
}

func newDfaDirectory() *reTrieDirectory {
	return &reTrieDirectory{
		table: map[dfaId]*reTrieNode{},
	}
}

func (directory *reTrieDirectory) addNode(source *node.Node) *reTrieNode {
	if directory == nil {
		// The new node cannot be indexed.
		return newReTrieNode(directory, NO_ID, source)
	} else if directory.next >= 64 {
		panic("Directory is full")
	}
	dfaId := dfaId(1) << directory.next
	directory.next++
	dfaNode := newReTrieNode(directory, dfaId, source)
	directory.table[dfaId] = dfaNode
	return dfaNode
}

func (directory *reTrieDirectory) copy(source *reTrieNode) *reTrieNode {
	result := directory.addNode(source.rootNode.Copy())
	return directory.merge(result, source)
}

func (directory *reTrieDirectory) ensureNode(given *reTrieNode) *reTrieNode {
	if given == nil {
		return directory.addNode(node.NewNode())
	}
	return given
}

func (directory *reTrieDirectory) get(id dfaId, missingSetter func() *reTrieNode) *reTrieNode {
	node, found := directory.table[id]
	if found {
		return node
	}
	node = missingSetter()
	node.id = id
	directory.table[id] = node
	return node
}

func (directory *reTrieDirectory) getMerged(a *reTrieNode, b *reTrieNode) (result *reTrieNode, exists bool) {
	if directory != a.directory && a.directory == b.directory {
		// Both a and b belong to a different directory. Reroute there.
		return a.directory.getMerged(a, b)
	}
	mergedId := a.id | b.id
	if a.id == NO_ID || b.id == NO_ID || a.directory != b.directory {
		// Embedded or foreign nodes.
		mergedId = NO_ID
	} else {
		// Valid merger.
		result, exists = directory.table[mergedId]
	}
	if !exists {
		result = newReTrieNode(directory, mergedId, a.Root().Copy())
		result.Root().Union(b.Root())
		if mergedId != NO_ID {
			directory.table[mergedId] = result
		}
	}
	return result, exists
}

func (directory *reTrieDirectory) linker(parent *reTrieNode, child *reTrieNode, re *syntax.Regexp, repeats bool) *reTrieNode {
	switch re.Op {
	case syntax.OpAlternate:
		parent = directory.ensureNode(parent)
		for _, alternative := range re.Sub {
			parent = directory.linker(parent, child, alternative, repeats)
		}
		return parent
	case syntax.OpAnyChar, syntax.OpAnyCharNotNL:
		parent = directory.ensureNode(parent)
		return parent.linkAnyChar(child, repeats)
	case syntax.OpBeginLine, syntax.OpEndLine, syntax.OpBeginText, syntax.OpEndText:
		if parent != nil {
			return parent
		}
		return child
	case syntax.OpCapture: // (xyz)
		if len(re.Sub) != 1 {
			panic("Unable to handle OpCapture with 2+ Sub options")
		} else if len(re.Name) == 0 {
			// Do nothing; return later.
		} else if re.Name[0] == '$' {
			embeddedNode := resolve(re.Name)
			if embeddedNode == nil {
				panic(fmt.Sprintf("Embeded node '%s' not found", re.Name))
			}
			parent = directory.ensureNode(parent)
			parent.linkEmbeddedNode(embeddedNode, child, repeats)
			return parent
		} else if re.Name[0] == '<' {
			parent = directory.ensureNode(parent)
			return parent.linkAnagram(re.Sub[0], child, repeats)
		}
		captureIndex := re.Cap - 1 // Standard library normally reserves 0 for entire string.
		child.capture(captureIndex*2 + 1)
		result := directory.linker(parent, child, re.Sub[0], repeats)
		result.capture(captureIndex * 2)
		return result
	case syntax.OpCharClass: // [xyz]
		parent = directory.ensureNode(parent)
		return parent.linkRunes(re.Rune, child, repeats)
	case syntax.OpConcat: // {parent} -> re.Sub -> {child}
		i := len(re.Sub)
		for i > 0 {
			i--
			if i == 0 {
				parent = directory.linker(parent, child, re.Sub[i], repeats)
			} else {
				child = directory.linker(nil, child, re.Sub[i], repeats)
			}
		}
		return parent
	case syntax.OpEmptyMatch:
		if parent == nil {
			return child
		}
		// Allow skipping straight to child.
		return directory.merge(parent, child)
	case syntax.OpLiteral: // x
		parent = directory.ensureNode(parent)
		return parent.linkPath(string(re.Rune), child, repeats)
	case syntax.OpPlus:
		if len(re.Sub) != 1 {
			panic("Unable to handle OpPlus with 2+ Sub options")
		} else if parent != nil {
			// We must not contaminate child which may be used by others.
			child = directory.copy(child)
		}
		// Only allow looping through child.
		directory.linker(child, child, re.Sub[0], true)
		// Require at least one path through re.Sub[0]
		return directory.linker(parent, child, re.Sub[0], repeats)
	case syntax.OpQuest: // x?
		if len(re.Sub) != 1 {
			panic("Unable to handle OpQuest with 2+ Sub options")
		}
		// Offer link to alternate path.
		parent = directory.linker(parent, child, re.Sub[0], repeats)
		// Mark the path to child as optional.
		return directory.merge(parent, child)
	case syntax.OpStar: // x*
		if len(re.Sub) != 1 {
			panic("Unable to handle OpStar with 2+ Sub options")
		}
		parent = directory.ensureNode(parent)
		// We must not contaminate child which may be used by others.
		detour := directory.copy(child)
		// Create a branching path which repeats.
		directory.linker(detour, detour, re.Sub[0], true)
		// Link from parent to this branch.
		directory.linker(parent, detour, re.Sub[0], repeats)
		// Ensure it is possible to go straight from parent to child.
		return directory.merge(parent, child)
	}
	panic(fmt.Sprintf("Unsupported instruction: %d", re.Op))
}

func (directory *reTrieDirectory) merge(a *reTrieNode, b *reTrieNode) *reTrieNode {
	result, exists := directory.getMerged(a, b)
	if !exists {
		result.mergeNode(a)
		result.mergeNode(b)
	}
	return result
}

func (directory *reTrieDirectory) split(link *reTrieLink) *reTrieLink {
	prefixRune, prefixRuneSize := utf8.DecodeRuneInString(link.prefix)
	parent := directory.addNode(node.NewNode())
	parent.linkPath(link.prefix[prefixRuneSize:], link.node, false)
	return newReTrieLinkFromRunes([]rune{prefixRune, prefixRune}, parent)
}
