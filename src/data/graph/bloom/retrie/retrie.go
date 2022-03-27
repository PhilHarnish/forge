package retrie

import (
	"fmt"
	"regexp"
	"regexp/syntax"

	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/query"
	"github.com/philharnish/forge/src/data/graph/bloom/weight"
)

type reTrie struct {
	root          *reTrieNode
	original      *regexp.Regexp // Used in Metadata().
	captureNames  []string
	directory     *reTrieDirectory
	embeddedNodes embeddedNodesMap
}

type embeddedNodesMap = map[string]node.NodeIterator

var embeddedNodeNameRegexp = regexp.MustCompile(`^{[^}]+}?`)

var embeddedRunes = []rune(".*?")

func NewReTrie(regularExpression string, matchWeight weight.Weight) *reTrie {
	re, err := syntax.Parse(regularExpression, syntax.Perl)
	if err != nil {
		panic(err)
	}
	captureNames := processCaptureNames(re.CapNames())

	embeddedNodes := embeddedNodesMap{}
	processSpecialOpCodes(re, embeddedNodes)
	re = re.Simplify()
	directory := newDfaDirectory()
	matchNode := directory.addNode(node.NewNode(matchWeight))
	rootTrieNode := directory.linker(nil, matchNode, re, false)

	return &reTrie{
		root:          rootTrieNode,
		original:      regexp.MustCompile(regularExpression),
		captureNames:  captureNames,
		directory:     directory,
		embeddedNodes: embeddedNodes,
	}
}

func (root *reTrie) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return root.root.Items(acceptor)
}

func (root *reTrie) Root() *node.Node {
	return root.root.Root()
}

func (root *reTrie) Header() query.QueryRowHeader {
	return root
}

func (root *reTrie) Labels() []string {
	return root.captureNames
}

func (root *reTrie) Metadata(path string) []weight.WeightedString {
	if len(root.captureNames) == 0 {
		return nil
	}
	submatches := root.original.FindStringSubmatch(path)
	result := make([]weight.WeightedString, len(submatches)-1)
	for i, submatch := range submatches[1:] {
		result[i].String = submatch
		result[i].Weight = 1
	}
	return result
}

func (root *reTrie) String() string {
	return root.root.String()
}

var anagramRe = regexp.MustCompile(`<[^<>]+>`)
var embeddedNodeRegexp = regexp.MustCompile(`\${[\w]+}`)

func processCaptureNames(captureNames []string) []string {
	captureNames = captureNames[1:]
	for i, name := range captureNames {
		if name == "" {
			captureNames[i] = fmt.Sprintf("%d", i+1)
		} else {
			captureNames[i] = name
		}
	}
	return captureNames
}

func processSpecialOpCodes(re *syntax.Regexp, embeddedNodes embeddedNodesMap) {
	for position := 0; position < len(re.Sub); position++ {
		child := re.Sub[position]
		if len(child.Sub) > 0 {
			processSpecialOpCodes(child, embeddedNodes)
		}
		position = maybeConsumeChildNode(re, position)
	}
}

func maybeConsumeChildNode(re *syntax.Regexp, position int) (nextPosition int) {
	nextPosition = position
	embeddedNodeChild := re.Sub[position]
	if embeddedNodeChild.Op != syntax.OpEndText {
		return nextPosition
	}
	// Implement ${...}{min, max}
	if position+1 >= len(re.Sub) {
		return nextPosition
	}
	position++
	literalChild := re.Sub[position]
	if literalChild.Op != syntax.OpLiteral {
		return nextPosition
	}
	match := embeddedNodeNameRegexp.FindStringIndex(string(literalChild.Rune))
	if match == nil {
		return nextPosition
	}
	start, end := match[0], match[1]
	name := ""
	substitutePosition := nextPosition
	substituteChild := re.Sub[substitutePosition]
	if literalChild.Rune[end-1] == '}' {
		// Already valid.
		name = "$" + string(literalChild.Rune[start:end])
		// Patch literal child's name (may be no-op).
		literalChild.Rune = literalChild.Rune[end:]
	} else if position+1 < len(re.Sub) {
		// Attempt to patch a missing "}" from "}{x,y}" syntax.
		position++
		repeatChar := retrieReRepeatChar(re, position)
		if repeatChar == '}' {
			name = "$" + string(literalChild.Rune[start:end]) + "}"
			// Replace the embedded node with the OpRepeat.
			substituteChild = re.Sub[position]
			substituteChild.Sub0[0] = embeddedNodeChild
			substituteChild.Sub = substituteChild.Sub0[:]
			nextPosition = position + 1
			// Rewrite re.Sub.
			re.Sub[substitutePosition] = substituteChild
			newLength := len(re.Sub) - (nextPosition - substitutePosition)
			copy(re.Sub[substitutePosition+1:], re.Sub[nextPosition:])
			re.Sub = re.Sub[:newLength+1]
		}
	}
	if name == "" {
		// Not valid.
		return nextPosition
	}
	// Rewrite embeddedNodeChild to be embedded node.
	embeddedNodeChild.Op = syntax.OpCapture
	embeddedNodeChild.Name = name
	embeddedNodeChild.Rune = nil
	embeddedNodeChild.Cap = 1
	embeddedNodeChild.Sub0[0] = &syntax.Regexp{
		Op:   syntax.OpLiteral,
		Rune: []rune(name),
	}
	embeddedNodeChild.Sub = embeddedNodeChild.Sub0[:]
	return substitutePosition
}

func retrieReRepeatChar(re *syntax.Regexp, position int) rune {
	if position > len(re.Sub) {
		return 0
	}
	child := re.Sub[position]
	if child.Op == syntax.OpRepeat && len(child.Sub) > 0 &&
		child.Sub[0].Op == syntax.OpLiteral {
		childChild := child.Sub[0]
		if len(childChild.Rune) == 1 {
			return childChild.Rune[0]
		}
	}
	return 0
}
