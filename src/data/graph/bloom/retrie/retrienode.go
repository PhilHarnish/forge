package retrie

import (
	"container/heap"
	"unicode"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/op"
)

type reTrieNode struct {
	directory    *reTrieDirectory
	id           dfaId
	rootNode     *node.Node
	links        reTrieLinks
	edgeMask     mask.Mask
	overlapping  mask.Mask
	embeddedNode node.NodeIterator
}

func newReTrieNode(directory *reTrieDirectory, id dfaId, root *node.Node) *reTrieNode {
	return &reTrieNode{
		directory: directory,
		id:        id,
		rootNode:  root,
		links:     reTrieLinks{},
	}
}

func (root *reTrieNode) Items(acceptor node.NodeAcceptor) node.NodeItems {
	if root.embeddedNode != nil && len(root.links) == 0 {
		// Optimized path: simply expand embeddedNode.
		return root.embeddedNode.Items(acceptor)
	}
	root.fixLinks()
	return newTrieItems(acceptor, root)
}

func (root *reTrieNode) Root() *node.Node {
	return root.rootNode
}

func (root *reTrieNode) String() string {
	return node.Format("ReTrie", root.Root())
}

func (root *reTrieNode) linkAnyChar(child *reTrieNode, repeats bool) *reTrieNode {
	root.rootNode.MaskEdgeMaskToChild(mask.ALL, child.rootNode)
	if repeats {
		root.rootNode.RepeatLengthMask(1)
	}
	root.addLink(newReTrieLinkFromRunes(mask.AlphabetRuneRanges, child))
	return root
}

func (root *reTrieNode) linkEmbeddedNode(embeddedNode node.NodeIterator, child *reTrieNode, repeats bool) *reTrieNode {
	if repeats {
		embeddedNode.Root().RepeatLengthMask(-1)
	}
	embeddedNode = op.Concat(embeddedNode, child)
	if root.embeddedNode == nil {
		root.embeddedNode = embeddedNode
	} else {
		root.embeddedNode = op.Or(root.embeddedNode, embeddedNode)
	}
	// Note: Linking must be additive; union root nodes.
	root.rootNode.Union(root.embeddedNode.Root())
	return root
}

func (root *reTrieNode) linkPath(path string, child *reTrieNode, repeats bool) *reTrieNode {
	err := root.rootNode.MaskPathToChild(path, child.rootNode)
	if err != nil {
		panic(err)
	} else if repeats {
		root.rootNode.RepeatLengthMask(len(path))
	}
	root.addLink(newReTrieLinkForPrefix(path, child))
	return root
}

func (root *reTrieNode) linkRunes(runes []rune, child *reTrieNode, repeats bool) *reTrieNode {
	if len(runes)%2 != 0 {
		panic("linkRunes does not support an odd number of runes")
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
	root.rootNode.MaskEdgeMaskToChild(pathMask, child.rootNode)
	if repeats {
		root.rootNode.RepeatLengthMask(1)
	}
	root.addLink(newReTrieLink(filteredRunes, child, pathMask))
	return root
}

func (root *reTrieNode) mergeNode(other *reTrieNode) {
	if root.embeddedNode != nil || other.embeddedNode != nil {
		panic("Merging embedded nodes not implemented.")
	}
	other.fixLinks()
	root.overlapping |= root.edgeMask & other.edgeMask
	root.edgeMask |= other.edgeMask
	root.links = append(root.links, other.links...)
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
	items := root.embeddedNode.Items(node.NodeAcceptAll)
	for items.HasNext() {
		path, item := items.Next()
		reTrieItem, okay := item.(*reTrieNode)
		if okay {
			root.linkPath(path, reTrieItem, false)
		} else {
			panic("Only able to expand reTrieNode")
		}
	}
	root.embeddedNode = nil
}

func (root *reTrieNode) fixLinks() {
	root.expandEmbeddedNode()
	if root.overlapping == 0 {
		return
	}
	overlapping := root.overlapping
	filtered, linkHeap := filterLinks(root.directory, overlapping, root.links)
	root.links = filtered
	newNodes := []*reTrieNode{}
	for len(linkHeap) > 0 {
		first := linkHeap.Next()
		// First, confirm there are any remaining edges to compare with.
		// Also check if the first edge is non-overlapping.
		if len(linkHeap) == 0 {
			root.links = append(root.links, first) // Finished; add and continue.
			continue
		}
		// Edge has exactly one batch; this is a confirmed hit.
		second := linkHeap.Next()
		firstDestination := first.node
		secondDestination := second.node
		if firstDestination.id == secondDestination.id {
			// Both edges go to the same place; return super-set of the range.
			var batch0 []rune
			if first.edgeMask&second.edgeMask == 0 { // Non-overlapping.
				batch0 = []rune{
					first.runes[0], first.runes[1], // First set
					second.runes[0], second.runes[1], // Then second set
				}
			} else { // Overlapping
				batch0 = []rune{
					min(first.runes[0], second.runes[0]),
					max(first.runes[1], second.runes[1]),
				}
			}
			root.links = append(root.links, newReTrieLinkFromRunes(batch0, first.node))
			continue
		} else if first.edgeMask&second.edgeMask == 0 {
			// Non-overlapping. Add first, return second and try again.
			root.links = append(root.links, first)
			heap.Push(&linkHeap, second)
			continue
		} else if first.runes[0] < second.runes[0] {
			// Batch #1 will begin and end before second edge starts.
			batch1 := []rune{first.runes[0], second.runes[0] - 1}
			root.links = append(root.links, newReTrieLinkFromRunes(batch1, first.node))
		}
		// The second batch is the portion which overlaps.
		overlapEnd := min(first.runes[1], second.runes[1])
		batch2 := []rune{second.runes[0], overlapEnd}
		merged, exists := root.directory.get(firstDestination, secondDestination)
		overlapEdge := newReTrieLinkFromRunes(batch2, merged)
		if !exists {
			newNodes = append(newNodes, merged, firstDestination, secondDestination)
		}
		if len(linkHeap) > 0 && linkHeap[0].edgeMask&overlapEdge.edgeMask != 0 {
			// Unfortunately, this overlaping portion overlaps with yet-more edges.
			// Return for further processing.
			heap.Push(&linkHeap, overlapEdge)
		} else {
			root.links = append(root.links, overlapEdge)
		}
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
			remainingEdge := newReTrieLinkFromRunes(batch3, destination)
			if len(linkHeap) > 0 && linkHeap[0].edgeMask&remainingEdge.edgeMask != 0 {
				// Unfortunately, this remaining portion overlaps with yet-more edges.
				// Return for further processing.
				heap.Push(&linkHeap, remainingEdge)
			} else {
				root.links = append(root.links, remainingEdge)
			}
		} // Else: Both ended at the same time; there isn't a 3rd batch.
	}
	for i := 0; i < len(newNodes); i += 3 {
		parent := newNodes[i]
		parent.mergeNode(newNodes[i+1])
		parent.mergeNode(newNodes[i+2])
	}
	root.overlapping = 0
}

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
			for i := 0; i < len(runes); i += 2 {
				batchEdge := newReTrieLinkFromRunes(runes[i:i+2], link.node)
				if batchEdge.edgeMask&overlapping == 0 {
					// This batch is OK.
					filtered = append(filtered, batchEdge)
				} else {
					links = append(links, batchEdge) // Reprocess.
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
