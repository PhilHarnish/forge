package retrie

import (
	"container/heap"
	"unicode"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
)

type reTrieNode struct {
	directory   *reTrieDirectory
	id          dfaId
	rootNode    *node.Node
	links       reTrieLinkList
	edgeMask    mask.Mask
	overlapping mask.Mask
}

type reTrieLink struct {
	prefix   string
	runes    []rune
	node     *reTrieNode
	edgeMask mask.Mask
}

func newReTrieLinkFromRunes(runes []rune, node *reTrieNode) *reTrieLink {
	edgeMask, err := mask.AlphabetMaskRanges(runes)
	if err != nil {
		panic(err)
	}
	return &reTrieLink{
		runes:    runes,
		node:     node,
		edgeMask: edgeMask,
	}
}

func newReTrieLinkForPrefix(prefix string, node *reTrieNode) *reTrieLink {
	prefixRune, _ := utf8.DecodeRuneInString(prefix)
	edgeMask, _ := mask.AlphabetMask(prefixRune)
	return &reTrieLink{
		prefix:   prefix,
		runes:    []rune{prefixRune, prefixRune},
		node:     node,
		edgeMask: edgeMask,
	}
}

type reTrieLinkList []*reTrieLink

func newReTrieNode(directory *reTrieDirectory, id dfaId, root *node.Node) *reTrieNode {
	return &reTrieNode{
		directory: directory,
		id:        id,
		rootNode:  root,
		links:     reTrieLinkList{},
	}
}

func (root *reTrieNode) Items(acceptor node.NodeAcceptor) node.NodeItems {
	root.splitEdges()
	return newTrieItems(acceptor, root)
}

func (root *reTrieNode) Root() *node.Node {
	return root.rootNode
}

func (root *reTrieNode) String() string {
	return node.Format("ReTrie", root.Root())
}

func (root *reTrieNode) linkAnyChar(child *reTrieNode, repeats bool) *reTrieNode {
	root.rootNode.ProvideMask = mask.ALL
	root.rootNode.MaskDistanceToChild(1, child.rootNode)
	if repeats {
		root.rootNode.RepeatLengthMask(1)
	}
	root.addLink(newReTrieLinkFromRunes(mask.AlphabetRuneRanges, child))
	return root
}

func (root *reTrieNode) linkPath(path string, child *reTrieNode, repeats bool) *reTrieNode {
	root.rootNode.MaskPathToChild(path, child.rootNode)
	if repeats {
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
	root.addLink(&reTrieLink{
		runes:    filteredRunes,
		node:     child,
		edgeMask: pathMask,
	})
	return root
}

func (root *reTrieNode) mergeNode(other *reTrieNode) {
	root.overlapping |= (root.edgeMask & other.edgeMask)
	root.links = append(root.links, other.links...)
	root.edgeMask |= other.edgeMask
}

func (root *reTrieNode) addLink(link *reTrieLink) {
	edgeMask := link.edgeMask
	overlapping := edgeMask & root.edgeMask
	if overlapping == 0 {
		root.edgeMask |= edgeMask
		// Optimized simple case.
		root.links = append(root.links, link)
		return
	}
	root.overlapping |= overlapping
	root.links = append(root.links, link)
	root.edgeMask |= edgeMask
}

func (root *reTrieNode) optionalPath(child *reTrieNode) *reTrieNode {
	return root.directory.merge(root, child)
}

func (root *reTrieNode) splitEdges() {
	if root.overlapping == 0 {
		return
	}
	overlapping := root.overlapping
	original := root.links
	root.links = make(reTrieLinkList, 0, len(original)*2)
	heap.Init(&original)
	newNodes := []*reTrieNode{}
	for len(original) > 0 {
		first := original.Next()
		// First, confirm there are any remaining edges to compare with.
		if len(original) == 0 {
			root.links = append(root.links, first) // Finished; add and continue.
			continue
		}
		// Next, confirm this edge was problematic.
		if first.edgeMask&overlapping == 0 {
			root.links = append(root.links, first) // No issue; add and continue.
			continue
		}
		// Next, split any edges with multiple rune blocks.
		if len(first.runes) > 2 {
			runes := first.runes
			for i := 0; i < len(runes); i += 2 {
				batchEdge := newReTrieLinkFromRunes(runes, first.node)
				batchMask := batchEdge.edgeMask
				if batchMask&overlapping == 0 {
					// This batch is OK.
					root.links = append(root.links, batchEdge)
				} else {
					// This batch needs to be reprocessed.
					heap.Push(&original, batchEdge)
				}
			}
			continue
		}
		// Similarly, split split apart prefix into pieces.
		if len(first.prefix) > 1 {
			first = root.directory.split(first)
		}
		// Edge has exactly one batch; this is a confirmed hit.
		second := original.Next()
		if len(second.runes) > 2 {
			// Similarly, split split apart prefix into pieces.
			panic("Splitting the second link is not implemented.")
		}
		if len(second.prefix) > 1 {
			second = root.directory.split(second)
		}

		firstDestination := first.node
		secondDestination := second.node
		if firstDestination.id == secondDestination.id {
			// Both edges go to the same place; return super-set of the range.
			batch0 := []rune{
				min(first.runes[0], second.runes[0]),
				max(first.runes[1], second.runes[1]),
			}
			root.links = append(root.links, newReTrieLinkFromRunes(batch0, first.node))
			continue
		}
		if first.edgeMask&second.edgeMask == 0 {
			panic("Heap should have brought overlapping edges together")
		}
		if first.runes[0] < second.runes[0] {
			// Batch #1 will begin and end before second edge starts.
			batch1 := []rune{first.runes[0], second.runes[0] - 1}
			root.links = append(root.links, newReTrieLinkFromRunes(batch1, first.node))
		}
		// The second batch is the portion which overlaps.
		overlapEnd := min(first.runes[1], second.runes[1])
		batch2 := []rune{second.runes[0], overlapEnd}
		merged := root.directory.partialMerge(firstDestination, secondDestination)
		overlapEdge := newReTrieLinkFromRunes(batch2, merged)
		newNodes = append(newNodes, merged, firstDestination, secondDestination)
		if len(original) > 0 && original[0].edgeMask&overlapEdge.edgeMask != 0 {
			// Unfortunately, this overlaping portion overlaps with yet-more edges.
			// Return for further processing.
			heap.Push(&original, overlapEdge)
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
			if len(original) > 0 && original[0].edgeMask&remainingEdge.edgeMask != 0 {
				// Unfortunately, this remaining portion overlaps with yet-more edges.
				// Return for further processing.
				heap.Push(&original, remainingEdge)
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

func (edges reTrieLinkList) Len() int {
	return len(edges)
}

func (edges reTrieLinkList) Less(i int, j int) bool {
	if edges[i].runes[0] == edges[j].runes[0] {
		return edges[i].runes[1] < edges[j].runes[1]
	}
	return edges[i].runes[0] < edges[j].runes[0]
}

func (h reTrieLinkList) Swap(i int, j int) {
	h[i], h[j] = h[j], h[i]
}

func (h *reTrieLinkList) Push(item interface{}) {
	*h = append(*h, item.(*reTrieLink))
}

func (h *reTrieLinkList) Pop() interface{} {
	original := *h
	end := len(original) - 1
	result := original[end]
	*h = original[:end]
	return result
}

func (h *reTrieLinkList) Next() *reTrieLink {
	return heap.Pop(h).(*reTrieLink)
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
