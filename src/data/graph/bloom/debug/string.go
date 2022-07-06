package debug

import (
	"fmt"
	"math"
	"regexp"
	"strings"
	"unicode/utf8"

	"github.com/philharnish/forge/src/data/graph/bloom/mask"
	"github.com/philharnish/forge/src/data/graph/bloom/node"
	"github.com/philharnish/forge/src/data/graph/bloom/order"
)

var lengthMaskRemover = regexp.MustCompile(" [◌●]+·*")
var horizontalLineReplacer = strings.NewReplacer(
	"├", "╪",
	"│", "╪",
	"└", "╘",
	"·", "═",
	" ", "═",
)

func StringChildren(iterator node.NodeIterator, depth ...int) string {
	if len(depth) > 0 {
		return stringPathChildrenWithPrefix(iterator, "", "", depth[0])
	}
	return stringPathChildrenWithPrefix(iterator, "", "", 1)
}

func StringPath(iterator node.NodeIterator, path string) string {
	return stringPathChildrenWithPrefix(iterator, "", path, 0)
}

func stringPathChildrenWithPrefix(iterator node.NodeIterator, base string, remainingPath string, remaining int) string {
	nodeString := lengthMaskRemover.ReplaceAllLiteralString(iterator.String(), "")
	if remaining <= 0 && remainingPath == "" {
		return nodeString
	}
	results := []string{
		nodeString,
	}
	generator := NewTestGenerator()
	items := generator.Items(order.Alphabetized(iterator))
	getLinePrefix := func() (string, string) {
		line := "├"
		prefix := "│"
		if !items.HasNext() {
			line = "└"
			if base == "" {
				prefix = "·"
			} else {
				prefix = " "
			}
		}
		return base + line, base + prefix
	}
	if iterator.Root().LengthsMask > 1 {
		results = append(results, base+"│"+mask.LengthString(iterator.Root().LengthsMask))
	}
	seen := mask.Mask(0)
	lastWeight := math.Inf(1)
	for items.HasNext() {
		path, item := items.Next()
		edge, _ := utf8.DecodeRuneInString(path)
		edgeMask, err := mask.AlphabetMask(edge)
		line, prefix := getLinePrefix()
		prefix += strings.Repeat(" ", len(path)-1)
		matchString := " "
		if item.Root().Matches() {
			matchString = "●"
		}
		childRemainingPath := ""
		if strings.HasPrefix(remainingPath, path) {
			childRemainingPath = remainingPath[len(path):]
		}
		results = append(results, fmt.Sprintf("%s%s%s->%s",
			line, path, matchString, stringPathChildrenWithPrefix(item, prefix, childRemainingPath, remaining-1)))
		if remainingPath != "" && childRemainingPath == "" {
			// Child was not expanded. Summarize instead.
			childSummary := stringChildSummary(item)
			if childSummary != "" {
				results = append(results, fmt.Sprintf("%s└%s", prefix, childSummary))
			}
		}
		// Check for errors.
		horizontalLine := horizontalLineReplacer.Replace(prefix)
		if err != nil {
			results = append(results, fmt.Sprintf(`%s> Invalid path: %s`, horizontalLine, err.Error()))
		}
		if edgeMask&seen != 0 {
			results = append(results, fmt.Sprintf(`%s> Duplicate edge: %s`, horizontalLine, mask.MaskString(0, edgeMask&seen)))
		}
		currentWeight := item.Root().MaxWeight
		if currentWeight > lastWeight {
			results = append(results, fmt.Sprintf(`%s> Weights out of order: %g > %g`, horizontalLine, currentWeight, lastWeight))
		}
		lastWeight = currentWeight
		seen |= edgeMask
	}
	return strings.Join(results, "\n")
}

func stringChildSummary(iterator node.NodeIterator) string {
	items := node.NodeGenerateAll.Items(iterator)
	if !items.HasNext() {
		return ""
	}
	count := 0
	seen := mask.Mask(0)
	for items.HasNext() {
		path, _ := items.Next()
		count++
		edge, _ := utf8.DecodeRuneInString(path)
		edgeMask, err := mask.AlphabetMask(edge)
		if err != nil {
			panic(err)
		}
		seen |= edgeMask
	}
	return fmt.Sprintf("%d children: %s", count, mask.MaskString(seen, mask.NONE))
}
