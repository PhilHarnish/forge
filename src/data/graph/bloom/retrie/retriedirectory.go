package retrie

import (
	"fmt"
	"regexp/syntax"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type dfaId = int64

type reTrieDirectory struct {
	table     map[dfaId]*reTrieNode
	nextNfaId dfaId
}

func newDfaDirectory() *reTrieDirectory {
	result := &reTrieDirectory{
		table: make(map[int64]*reTrieNode),
	}
	return result
}

func (directory *reTrieDirectory) addRegexp(re *syntax.Regexp, source *node.Node) *reTrieNode {
	nfaId := directory.nextNfaId
	directory.nextNfaId++
	dfaId := dfaId(1) << nfaId
	dfaNode := newReTrieNode(directory, dfaId, source)
	directory.table[dfaId] = dfaNode
	return dfaNode
}

func (directory *reTrieDirectory) addRegexpAs(re *syntax.Regexp, source *reTrieNode) *reTrieNode {
	result := directory.addRegexp(re, source.rootNode.Copy())
	return directory.merge(result, source)
}

func (directory *reTrieDirectory) ensureNode(re *syntax.Regexp, given *reTrieNode) *reTrieNode {
	if given == nil {
		return directory.addRegexp(re, node.NewNode())
	}
	return given
}

func (directory *reTrieDirectory) linker(parent *reTrieNode, child *reTrieNode, re *syntax.Regexp, repeats bool) *reTrieNode {
	switch re.Op {
	case syntax.OpAlternate:
		parent = directory.ensureNode(re, parent)
		for _, alternative := range re.Sub {
			parent = directory.linker(parent, child, alternative, repeats)
		}
		return parent
	case syntax.OpAnyChar, syntax.OpAnyCharNotNL:
		parent = directory.ensureNode(re, parent)
		parent.linkAnyChar(child, repeats)
		return parent
	case syntax.OpBeginLine, syntax.OpEndLine, syntax.OpBeginText, syntax.OpEndText:
		if parent != nil {
			return parent
		}
		return child
	case syntax.OpCapture: // (xyz)
		if len(re.Sub) != 1 {
			panic("Unable to handle OpCapture with 2+ Sub options")
		}
		return directory.linker(parent, child, re.Sub[0], repeats)
	case syntax.OpCharClass: // [xyz]
		parent = directory.ensureNode(re, parent)
		return parent.linkRunes(re.Rune, child, repeats)
	case syntax.OpConcat: // xyz
		i := len(re.Sub)
		for i > 0 {
			i--
			parent, child = nil, directory.linker(parent, child, re.Sub[i], repeats)
		}
		return child
	case syntax.OpEmptyMatch:
		if parent == nil {
			return child
		}
		// Allow skipping straight to child.
		return parent.optionalPath(child)
	case syntax.OpLiteral: // x
		parent = directory.ensureNode(re, parent)
		parent.linkPath(string(re.Rune), child, repeats)
		return parent
	case syntax.OpPlus:
		if len(re.Sub) != 1 {
			panic("Unable to handle OpPlus with 2+ Sub options")
		} else if parent == nil {
			// Only allow looping through child.
			directory.linker(child, child, re.Sub[0], true)
			// Require at least one path through re.Sub[0]
			return directory.linker(parent, child, re.Sub[0], true)
		}
		// We must not contaminate child which may be used by others.
		detour := directory.addRegexpAs(re, child)
		// Child may optionally loop back to itself.
		directory.linker(detour, detour, re.Sub[0], true)
		// Require at least one path through re.Sub[0]
		directory.linker(parent, detour, re.Sub[0], true)
		return parent
	case syntax.OpQuest: // x?
		if len(re.Sub) != 1 {
			panic("Unable to handle OpQuest with 2+ Sub options")
		}
		// Offer link to alternate path.
		parent = directory.linker(parent, child, re.Sub[0], repeats)
		// Mark the path to child as optional.
		return parent.optionalPath(child)
	case syntax.OpStar: // x*
		if len(re.Sub) != 1 {
			panic("Unable to handle OpStar with 2+ Sub options")
		} else if parent == nil {
			// Only allow looping through child.
			return directory.linker(child, child, re.Sub[0], true)
		}
		// We must not contaminate parent which may be used by others.
		detour := directory.addRegexpAs(re, child)
		// Create a branching path to the detour via re.Sub[0]...
		directory.linker(parent, detour, re.Sub[0], true)
		// ...which repeats.
		directory.linker(detour, detour, re.Sub[0], true)
		// Ensure it is possible to go straight from parent to child.
		return directory.merge(parent, child)
	}
	panic(fmt.Sprintf("Unsupported instruction: %d", re.Op))
}

func (directory *reTrieDirectory) merge(a *reTrieNode, b *reTrieNode) *reTrieNode {
	mergedId := a.id | b.id
	mergedDfaNode, exists := directory.table[mergedId]
	if exists {
		return mergedDfaNode
	}
	result := directory.partialMerge(a, b)
	result.mergeNode(a)
	result.mergeNode(b)
	return result
}

func (directory *reTrieDirectory) partialMerge(a *reTrieNode, b *reTrieNode) *reTrieNode {
	mergedId := a.id | b.id
	mergedDfaNode, exists := directory.table[mergedId]
	if exists {
		return mergedDfaNode
	}
	result := newReTrieNode(directory, mergedId, a.rootNode.Copy())
	directory.table[mergedId] = result
	result.rootNode.Union(b.rootNode)
	return result
}

func (directory *reTrieDirectory) split(link *reTrieLink) *reTrieLink {
	prefixRune, prefixRuneSize := utf8.DecodeRuneInString(link.prefix)
	parent := directory.ensureNode(nil, nil)
	parent.linkPath(link.prefix[prefixRuneSize:], link.node, false)
	return newReTrieLinkFromRunes([]rune{prefixRune, prefixRune}, parent)
}
