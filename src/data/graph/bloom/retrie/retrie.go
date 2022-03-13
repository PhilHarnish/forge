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
	rootTrieNode *reTrieNode
	original     *regexp.Regexp
	captureNames []string
	instructions []*reTrieNode
	directory    *reTrieDirectory
}

const EPSILON_EXPANSION = true

func NewReTrie(regularExpression string, matchWeight weight.Weight) *reTrie {
	re, err := syntax.Parse(regularExpression, syntax.Perl)
	if err != nil {
		panic(err)
	}
	captureNames := processCaptureNames(re.CapNames())

	re = re.Simplify()
	directory := newDfaDirectory()
	matchNode := directory.addRegexp(nil, node.NewNode(matchWeight))
	var instructions []*reTrieNode
	rootTrieNode := directory.linker(nil, matchNode, re, false)

	return &reTrie{
		rootTrieNode: rootTrieNode,
		original:     regexp.MustCompile(regularExpression),
		captureNames: captureNames,
		instructions: instructions,
		directory:    directory,
	}
}

func (root *reTrie) Items(acceptor node.NodeAcceptor) node.NodeItems {
	return root.rootTrieNode.Items(acceptor)
}

func (root *reTrie) Root() *node.Node {
	return root.rootTrieNode.Root()
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
	return root.rootTrieNode.String()
}

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
