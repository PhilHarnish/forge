package retrie

import (
	"fmt"
	"regexp"
	"regexp/syntax"
	"strings"

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

const customNodeIdentifyingPrefix = "__RETRIE__"
const customNodeColonSubstitution = "__RETRIE_COLON__"
const matchedCaptureSubstitution = "__RETRIE_CAPTURE__"
const retrieAnagramStartMarker = "(?P<__RETRIE__ANAGRAM__>"
const retrieAnagramEndMarker = ")"

var anagramLiteral = regexp.MustCompile(`<[^>]+(>|$)`)
var embeddedNodeLiteral = regexp.MustCompile(`{[a-zA-Z_: ]+(}|$)`)
var expandedSyntaxLiteral = regexp.MustCompile(`<[^>]+(>|$)|{[a-zA-Z_: ]+(}|$)`)
var embeddedNodeNameRegexp = regexp.MustCompile(`^{[^}]+}?`)
var embeddedNodeRegexp = regexp.MustCompile(`{[a-zA-Z][\w: ]*}`)
var namedCaptureGroup = regexp.MustCompile(`\(?P<\w*>`)
var matchedCaptureSubstitutionRegexp = regexp.MustCompile(matchedCaptureSubstitution)
var embeddedRunes = []rune(".*?")

func NewReTrie(regularExpression string, matchWeight weight.Weight) *reTrie {
	regularExpression = preprocessRegularExpression(regularExpression)
	re, err := syntax.Parse(regularExpression, syntax.Perl)
	if err != nil {
		panic(err)
	}
	captureNames := processCaptureNames(re.CapNames())

	embeddedNodes := embeddedNodesMap{}
	re = processSpecialOpCodes(re, embeddedNodes)
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

func processCaptureNames(captureNames []string) []string {
	// TODO: Handle customNodeIdentifyingPrefix.
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

func processSpecialOpCodes(re *syntax.Regexp, embeddedNodes embeddedNodesMap) *syntax.Regexp {
	if strings.HasPrefix(re.Name, customNodeIdentifyingPrefix) {
		suffix := re.Name[len(customNodeIdentifyingPrefix):]
		re.Name = fmt.Sprintf("$%s", suffix)
	}
	for position := 0; position < len(re.Sub); position++ {
		child := re.Sub[position]
		if len(child.Sub) > 0 {
			processSpecialOpCodes(child, embeddedNodes)
		}
	}
	return re
}

func maybeSplitLiterals(parent *syntax.Regexp) *syntax.Regexp {
	if parent.Op == syntax.OpLiteral {
		literal := string(parent.Rune)
		if !anagramLiteral.MatchString(literal) && !embeddedNodeLiteral.MatchString(literal) {
			return parent
		}
		parent = &syntax.Regexp{
			Op:   syntax.OpConcat,
			Sub0: [1]*syntax.Regexp{parent},
		}
		parent.Sub = parent.Sub0[:]
	}
	if parent.Op != syntax.OpConcat {
		return parent
	}
	children := make([]*syntax.Regexp, 0, 2*len(parent.Sub))
	for position := 0; position < len(parent.Sub); position++ {
		child := parent.Sub[position]
		if child.Op != syntax.OpLiteral {
			children = append(children, child)
			continue
		}
		literal := string(child.Rune)
		matches := expandedSyntaxLiteral.FindAllStringIndex(literal, -1)
		if matches == nil {
			children = append(children, child)
			continue
		}
		suffix := findSuffixCharacter(parent, position+1)
		fmt.Println(literal, ":", matches, suffix)
		lastAppend := 0
		for _, match := range matches {
			substring := literal[match[0]:match[1]]
			fmt.Println("match:", substring)
			lastChar := substring[len(substring)-1]
			if substring[0] == '{' {
				if lastChar == '}' {
					// Already valid.
					children, lastAppend = maybeFlush(children, literal, lastAppend, match[0])
					captureChild := newEmbeddedRegexpNode(substring)
					children = append(children, captureChild)
					lastAppend = match[1]
				} else if suffix == '}' {
					// Reparent.
					children, lastAppend = maybeFlush(children, literal, lastAppend, match[0])
					captureChild := newEmbeddedRegexpNode(substring)
					// Skip past suffix operation.
					position++
					// Reuse suffix operation.
					suffixOp := parent.Sub[position]
					suffixOp.Sub0[0] = captureChild
					suffixOp.Sub = suffixOp.Sub0[:]
					children = append(children, suffixOp)
					lastAppend = match[1]
				}
			} else if substring[0] == '<' {
				if lastChar == '>' {
					// Already valid.
				} else if suffix == '>' {
					// Reparent.
				}
			}
		}
		end := len(literal)
		if lastAppend < end {
			// Flush.
			children = append(children, &syntax.Regexp{
				Op:   syntax.OpLiteral,
				Rune: []rune(literal[lastAppend:end]),
			})
		}
	}
	parent.Sub = children
	parent.Sub0[0] = children[0]
	return parent
}

func maybeFlush(children []*syntax.Regexp, literal string, start int, end int) ([]*syntax.Regexp, int) {
	if end > start {
		// Flush.
		children = append(children, &syntax.Regexp{
			Op:   syntax.OpLiteral,
			Rune: []rune(literal[start:end]),
		})
	}
	return children, end
}

func findSuffixCharacter(re *syntax.Regexp, position int) rune {
	if position >= len(re.Sub) {
		return 0
	}
	child := re.Sub[position]
	switch child.Op {
	case syntax.OpPlus, syntax.OpRepeat, syntax.OpQuest, syntax.OpStar:
		if len(child.Sub) > 0 && child.Sub[0].Op == syntax.OpLiteral {
			childChild := child.Sub[0]
			if len(childChild.Rune) == 1 {
				return childChild.Rune[0]
			}
		}
	}
	return 0
}

func newEmbeddedRegexpNode(name string) *syntax.Regexp {
	result := &syntax.Regexp{
		Op:   syntax.OpCapture,
		Name: name,
		Sub0: [1]*syntax.Regexp{
			{
				Op:   syntax.OpLiteral,
				Rune: []rune("xxx"),
			},
		},
	}
	result.Sub = result.Sub0[:]
	return result
}
func preprocessRegularExpression(regularExpression string) string {
	// First, hide all "?P<...>" expressions.
	matchedCaptures := []string{}
	regularExpression = namedCaptureGroup.ReplaceAllStringFunc(regularExpression, func(match string) string {
		matchedCaptures = append(matchedCaptures, match)
		return matchedCaptureSubstitution
	})
	// Next, replace all remaining < and > characters.
	regularExpression = strings.ReplaceAll(regularExpression, ">", retrieAnagramEndMarker)
	regularExpression = strings.ReplaceAll(regularExpression, "<", retrieAnagramStartMarker)
	// Restore "?P<...>" expressions.
	regularExpression = matchedCaptureSubstitutionRegexp.ReplaceAllStringFunc(regularExpression, func(match string) string {
		next := matchedCaptures[0]
		matchedCaptures = matchedCaptures[1:]
		return next
	})
	regularExpression = embeddedNodeRegexp.ReplaceAllStringFunc(regularExpression, func(match string) string {
		// Hide ":" characters from the parser.
		name := strings.ReplaceAll(match[1:len(match)-1], ":", customNodeColonSubstitution)
		return fmt.Sprintf("(?P<%s%s>)", customNodeIdentifyingPrefix, name)
	})
	return regularExpression
}
