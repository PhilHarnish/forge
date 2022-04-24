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
const retrieAnagramIdentifier = "__RETRIE_ANAGRAM__"
const retrieAnagramCaptureIdentifier = "__RETRIE_ANAGRAM_CAPTURE__"
const retrieAnagramStartMarker = "(?P<" + retrieAnagramIdentifier + ">"
const retrieAnagramEndMarker = ")"

var embeddedNodeRegexp = regexp.MustCompile(`{[a-zA-Z][\w: ]*}`)
var retrieSimpleAnagram = regexp.MustCompile(`<[a-z. ]{2,}>`)
var namedCaptureGroup = regexp.MustCompile(`\(?P<\w*>`)
var matchedCaptureSubstitutionRegexp = regexp.MustCompile(matchedCaptureSubstitution)

func NewReTrie(regularExpression string, matchWeight weight.Weight) *reTrie {
	regularExpression = preprocessRegularExpression(regularExpression)
	re, err := syntax.Parse(regularExpression, syntax.Perl)
	if err != nil {
		panic(err)
	}

	embeddedNodes := embeddedNodesMap{}
	re = processSpecialOpCodes(re, embeddedNodes, false)
	captureNames := processCaptureNames(re.CapNames())
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
	captureNames = captureNames[1:]
	out := 0
	for _, name := range captureNames {
		if name == "" {
			captureNames[out] = fmt.Sprintf("%d", out+1)
		} else if name == retrieAnagramCaptureIdentifier || name[0] == '<' {
			continue // Ignore automatic anagram capture groups.
		} else {
			captureNames[out] = name
		}
		out++
	}
	return captureNames[0:out]
}

func processSpecialOpCodes(re *syntax.Regexp, embeddedNodes embeddedNodesMap, inAnagram bool) *syntax.Regexp {
	if re.Name == retrieAnagramIdentifier {
		// Note: "<" prefix is significant.
		re.Name = fmt.Sprintf("<%s>", re.Sub[0].String())
		inAnagram = true // Overwrite child capture groups as they were auto-created.
	} else if strings.HasPrefix(re.Name, customNodeIdentifyingPrefix) {
		// Remove customNodeIdentifyingPrefix.
		suffix := re.Name[len(customNodeIdentifyingPrefix):]
		suffix = strings.ReplaceAll(suffix, customNodeColonSubstitution, ":")
		re.Name = fmt.Sprintf("$%s", suffix)
	} else if inAnagram && re.Op == syntax.OpCapture {
		re.Name = retrieAnagramCaptureIdentifier
	}
	for position := 0; position < len(re.Sub); position++ {
		child := re.Sub[position]
		if len(child.Sub) > 0 {
			processSpecialOpCodes(child, embeddedNodes, inAnagram)
		}
	}
	return re
}

func preprocessRegularExpression(regularExpression string) string {
	// First, hide all "?P<...>" expressions.
	matchedCaptures := []string{}
	regularExpression = namedCaptureGroup.ReplaceAllStringFunc(regularExpression, func(match string) string {
		matchedCaptures = append(matchedCaptures, match)
		return matchedCaptureSubstitution
	})
	// Next, process remaining < and > characters as anagram expression.
	regularExpression = retrieSimpleAnagram.ReplaceAllStringFunc(regularExpression, func(match string) string {
		result := strings.Builder{}
		result.WriteString("<(") // <
		result.WriteByte(match[1])
		// Automatically convert "<abc>" to "<(a)(b)(c)>" to match Nutrimatic behavior.
		for _, c := range match[2 : len(match)-1] {
			result.WriteString(")(")
			result.WriteRune(c)
		}
		result.WriteString(")>")
		return result.String()
	})
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
