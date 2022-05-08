package retrie

import (
	"container/heap"
	"regexp/syntax"
	"unicode"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
	"github.com/philharnish/forge/src/data/slices"
)

type reTrieNode struct {
	directory    *reTrieDirectory
	id           dfaId
	rootNode     *node.Node
	links        reTrieLinks
	edgeMask     mask.Mask
	overlapping  mask.Mask
	embeddedNode node.NodeIterator
	captures     []int
}

func newReTrieNode(directory *reTrieDirectory, id dfaId, root *node.Node) *reTrieNode {
	return &reTrieNode{
		directory: directory,
		id:        id,
		rootNode:  root,
		links:     reTrieLinks{},
	}
}

func newEmbeddedReTrieNode(embeddedNode node.NodeIterator) *reTrieNode {
	return &reTrieNode{
		embeddedNode: embeddedNode,
	}
}

func (root *reTrieNode) Items(generator node.NodeGenerator) node.NodeItems {
	if root.embeddedNode != nil && len(root.links) == 0 && len(root.captures) == 0 {
		// Optimized path: simply use embeddedNode.
		return generator.Items(root.embeddedNode)
	}
	root.expandLinks()
	return newTrieItems(generator, root)
}

func (root *reTrieNode) Root() *node.Node {
	if root.rootNode == nil && root.embeddedNode != nil {
		if len(root.links) != 0 {
			panic("Unable to expand Root when links are present")
		}
		root.rootNode = root.embeddedNode.Root().Copy()
	}
	return root.rootNode
}

func (root *reTrieNode) String() string {
	if root.embeddedNode != nil && len(root.links) == 0 {
		// Optimized path: simply expand embeddedNode.
		return root.embeddedNode.String()
	}
	root.expandLinks()
	return node.Format("ReTrie", root.Root())
}

func (root *reTrieNode) capture(position int) {
	captures := []int{position}
	if root.captures == nil {
		root.captures = captures
	} else {
		root.captures = slices.MergeInts(root.captures, captures)
	}
}

func (root *reTrieNode) linkAnagram(options *syntax.Regexp, child *reTrieNode, repeats bool) *reTrieNode {
	if options.Op != syntax.OpConcat {
		panic("linkAnagram requires OpConcat")
	}
	return newReTrieAnagramNodeParent(root, options.Sub, child, repeats)
}

func (root *reTrieNode) linkAnyChar(child *reTrieNode, repeats bool) *reTrieNode {
	root.Root().MaskEdgeMaskToChild(mask.ALL, child.Root())
	if repeats {
		root.Root().RepeatLengthMask(1)
	}
	root.addLink(newReTrieLinkFromRunes(mask.AlphabetRuneRanges, child))
	return root
}

func (root *reTrieNode) linkEmbeddedNode(embeddedNode node.NodeIterator, child *reTrieNode, repeats bool) *reTrieNode {
	if repeats {
		embeddedNode.Root().RepeatLengthMask(-1)
	}
	root.setEmbeddedNode(op.Concat(embeddedNode, child))
	return root
}

func (root *reTrieNode) linkPath(path string, child *reTrieNode, repeats bool) *reTrieNode {
	err := root.Root().MaskPathToChild(path, child.Root())
	if err != nil {
		panic(err)
	} else if repeats {
		root.Root().RepeatLengthMask(len(path))
	}
	root.addLink(newReTrieLinkForPrefix(path, child))
	return root
}

func (root *reTrieNode) linkRunes(runes []rune, child *reTrieNode, repeats bool) *reTrieNode {
	if len(runes)%2 != 0 {
		panic("linkRunes does not support an odd number of runes")
	}
	if runes[0] == 0 && runes[len(runes)-1] == unicode.MaxRune {
		// Clamp runes if they look like a negation (i.e. span [0, MaxRun]).
		runes = mask.ClampRunes(runes)
	}
	pathMask := mask.Mask(0b0)
	i := 0
	filteredRunes := make([]rune, 0, len(runes))
	for i < len(runes) {
		start := runes[i]
		end := runes[i+1]
		rangeMask, err := mask.AlphabetMaskRange(start, end)
		if err == nil {
			pathMask |= rangeMask
			filteredRunes = append(filteredRunes, runes[i], runes[i+1])
		} else if unicode.IsLetter(start) && unicode.IsLetter(end) {
			// A letter is a reasonable character to attempt; skip.
		} else if unicode.IsNumber(start) && unicode.IsNumber(end) {
			// A number is a reasonable character to attempt; skip.
		} else if start == '_' && end == '_' {
			// _ is a reasonable character to attempt; skip.
		} else {
			panic(err)
		}
		i += 2
	}
	root.Root().MaskEdgeMaskToChild(pathMask, child.Root())
	if repeats {
		root.Root().RepeatLengthMask(1)
	}
	root.addLink(newReTrieLink(filteredRunes, child, pathMask))
	return root
}

func (root *reTrieNode) mergeNode(other *reTrieNode) {
	root.setEmbeddedNode(other.embeddedNode)
	root.overlapping |= (root.edgeMask & other.edgeMask) | other.overlapping
	root.edgeMask |= other.edgeMask
	root.links = append(root.links, other.links...)
	root.captures = slices.MergeInts(root.captures, other.captures)
}

func (root *reTrieNode) setEmbeddedNode(embeddedNode node.NodeIterator) {
	if embeddedNode == nil {
		return
	} else if root.embeddedNode == nil {
		root.embeddedNode = embeddedNode
	} else {
		root.embeddedNode = op.Or(root.embeddedNode, embeddedNode)
	}
	// Note: Linking must be additive; union root nodes.
	root.Root().Union(root.embeddedNode.Root())
}

func (root *reTrieNode) addLink(link *reTrieLink) {
	root.overlapping |= link.edgeMask & root.edgeMask
	root.edgeMask |= link.edgeMask
	root.links = append(root.links, link)
}

func (root *reTrieNode) expandEmbeddedNode() {
	if root.embeddedNode == nil {
		return
	}
	items := node.NodeGenerateAll.Items(root.embeddedNode)
	for items.HasNext() {
		path, item := items.Next()
		reTrieItem, okay := item.(*reTrieNode)
		if !okay {
			reTrieItem = newReTrieNode(root.directory, 0, item.Root().Copy())
			reTrieItem.embeddedNode = item
		}
		root.linkPath(path, reTrieItem, false)
	}
	root.embeddedNode = nil
}

func (root *reTrieNode) expandLinks() {
	root.expandEmbeddedNode()
	root.fixLinks()
}

func (root *reTrieNode) fixLinks() {
	if root.overlapping == 0 {
		return
	}
	overlapping := root.overlapping
	filtered, linkHeap := filterLinks(root.directory, overlapping, root.links)
	root.links = filtered
	newNodes := []*reTrieNode{}
	var appendLink = func(link *reTrieLink) {
		if len(linkHeap) > 0 && overlapping&link.edgeMask != 0 {
			// Unfortunately, this overlaping portion overlaps with yet-more edges.
			// Return for further processing.
			heap.Push(&linkHeap, link)
		} else {
			root.links = append(root.links, link)
		}
	}
	for len(linkHeap) > 0 {
		first := linkHeap.Next()
		// First, confirm there are any remaining edges to compare with.
		// Also check if the first edge is non-overlapping.
		if len(linkHeap) == 0 {
			root.links = append(root.links, first) // Finished; add and continue.
			continue
		}
		// Operate on edge batch {first, second}.
		second := linkHeap.Next()
		firstDestination := first.node
		secondDestination := second.node
		if firstDestination.directory != nil && secondDestination.directory != nil &&
			firstDestination.directory == secondDestination.directory &&
			firstDestination.id == secondDestination.id &&
			first.edgeMask&second.edgeMask != 0 {
			// Both edges go to the same place and overlap.
			appendLink(newReTrieLinkFromRunes([]rune{
				min(first.runes[0], second.runes[0]),
				max(first.runes[1], second.runes[1]),
			}, first.node))
			continue
		} else if first.edgeMask&second.edgeMask == 0 {
			// Non-overlapping. Add first, return second and try again.
			root.links = append(root.links, first)
			heap.Push(&linkHeap, second)
			continue
		} else if first.runes[0] < second.runes[0] {
			// Batch #1 will begin and end before second edge starts.
			batch1 := []rune{first.runes[0], second.runes[0] - 1}
			appendLink(newReTrieLinkFromRunes(batch1, first.node))
		}
		// The second batch is the portion which overlaps.
		overlapEnd := min(first.runes[1], second.runes[1])
		batch2 := []rune{second.runes[0], overlapEnd}
		merged, exists := root.directory.getMerged(firstDestination, secondDestination)
		if !exists {
			newNodes = append(newNodes, merged, firstDestination, secondDestination)
		}
		appendLink(newReTrieLinkFromRunes(batch2, merged))
		// Assign the remaining rune range depending on which group is larger.
		if first.runes[1] != second.runes[1] {
			// Guess that the first rune is larger.
			remainderEnd := first.runes[1]
			destination := first.node
			if first.runes[1] < second.runes[1] { // Update if wrong.
				remainderEnd = second.runes[1]
				destination = second.node
			}
			batch3 := []rune{overlapEnd + 1, remainderEnd}
			appendLink(newReTrieLinkFromRunes(batch3, destination))
		} // Else: Both ended at the same time; there isn't a 3rd batch.
	}
	for i := 0; i < len(newNodes); i += 3 {
		parent := newNodes[i]
		parent.mergeNode(newNodes[i+1])
		parent.mergeNode(newNodes[i+2])
	}
	root.overlapping = 0
}

// Sort `links` into non-overlapping (filtered) and overlapping (linkHeap).
func filterLinks(directory *reTrieDirectory, overlapping mask.Mask, links reTrieLinks) (filtered reTrieLinks, linkHeap reTrieLinks) {
	filtered = make(reTrieLinks, 0, len(links)*2)
	linkHeap = make(reTrieLinks, 0, len(links)*2)
	for i := 0; i < len(links); i++ {
		link := links[i]
		if link.edgeMask&overlapping == 0 {
			// This link is non-overlapping.
			filtered = append(filtered, link)
		} else if len(link.runes) > 2 {
			// This link overlaps and has multiple rune blocks.
			runes := link.runes
			for j := 0; j < len(runes); j += 2 {
				batchEdge := newReTrieLinkFromRunes(runes[j:j+2], link.node)
				if batchEdge.edgeMask&overlapping == 0 {
					// This batch is OK.
					filtered = append(filtered, batchEdge)
				} else {
					linkHeap = append(linkHeap, batchEdge)
				}
			}
		} else { // Link overlaps
			if len(link.prefix) > 1 {
				// If there is a prefix, split it into [rune]+[prefix].
				link = directory.split(link)
			}
			linkHeap = append(linkHeap, link)
		}
	}
	heap.Init(&linkHeap)
	return filtered, linkHeap
}

func min(a rune, b rune) rune {
	if a < b {
		return a
	}
	return b
}

func max(a rune, b rune) rune {
	if a > b {
		return a
	}
	return b
}
