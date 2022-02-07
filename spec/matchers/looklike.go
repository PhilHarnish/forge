package matchers

import (
	"fmt"
	"strings"

	"github.com/onsi/gomega/types"
)

func LookLike(expected string) types.GomegaMatcher {
	return &lookLikeMatcher{expected: prepare(expected)}
}

type lookLikeMatcher struct {
	expected string
}

var whitespaceReplacer = strings.NewReplacer(
	" ", "␣",
	"\t", "⇥",
)

func (matcher *lookLikeMatcher) Match(actual interface{}) (success bool, err error) {
	if given, ok := actual.(string); ok {
		return matcher.expected == prepare(given), nil
	}
	return false, fmt.Errorf("LooksLike matcher expects a string")
}

func (matcher *lookLikeMatcher) FailureMessage(actual interface{}) (message string) {
	if given, ok := actual.(string); ok {
		return fmt.Sprintf("Expected\n%s\nto look like\n%s\n%s",
			prepare(given), matcher.expected, findDifference(given, matcher.expected))
	}
	return fmt.Sprintf("Expected\n%#v\nto look like\n%s", actual, matcher.expected)
}

func (matcher *lookLikeMatcher) NegatedFailureMessage(actual interface{}) (message string) {
	if given, ok := actual.(string); ok {
		return fmt.Sprintf("Expected\n%s\nnot to look like\n%s\n%s",
			prepare(given), matcher.expected, findDifference(given, matcher.expected))
	}
	return fmt.Sprintf("Expected\n%#v\nnot to look like\n%s", actual, matcher.expected)
}

func prepare(s string) string {
	return dedent(strings.Trim(s, "\n"))
}

func findDifference(a string, b string) string {
	aLines := strings.Split(whitespaceReplacer.Replace(prepare(a)), "\n")
	bLines := strings.Split(whitespaceReplacer.Replace(prepare(b)), "\n")
	minLines := len(aLines)
	if len(bLines) < minLines {
		minLines = len(bLines)
	}
	for i, aLine := range aLines[:minLines] {
		bLine := bLines[i]
		if aLine == bLine {
			continue
		}
		return fmt.Sprintf("Difference:\n%s\n%s", aLine, bLine)
	}
	return fmt.Sprintf("Remaining lines:\n%s\nAnd:\n%s",
		strings.Join(aLines[minLines:], "↵"), strings.Join(bLines[minLines:], "↵"))
}

func dedent(s string) string {
	shortestIndent := len(s)
	lines := strings.Split(s, "\n")
	// First pass to find the longest run of whitespace.
	firstLineWithText := len(lines) - 1
	lastLineWithText := 0
	for i, line := range lines {
		indentSize := 0
		hasText := false
		for _, c := range line {
			if c == ' ' || c == '\t' {
				indentSize++
			} else {
				hasText = true
				break
			}
		}
		if !hasText {
			continue
		}
		if i < firstLineWithText {
			firstLineWithText = i
		}
		if i > lastLineWithText {
			lastLineWithText = i
		}
		if indentSize < shortestIndent {
			shortestIndent = indentSize
		}
	}
	result := []string{}
	for _, line := range lines[firstLineWithText : lastLineWithText+1] {
		start := shortestIndent
		if start > len(line) {
			start = len(line)
		}
		result = append(result, strings.TrimRight(line[start:], "\t "))
	}
	return strings.Join(result, "\n")
}
