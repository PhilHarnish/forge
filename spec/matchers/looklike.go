package matchers

import (
	"fmt"
	"strings"

	"github.com/onsi/gomega/types"
)

func LookLike(expected string) types.GomegaMatcher {
	return &lookLikeMatcher{expected: expected}
}

type lookLikeMatcher struct {
	expected string
}

func (matcher *lookLikeMatcher) Match(actual interface{}) (success bool, err error) {
	given, ok := actual.(string)
	if !ok {
		return false, fmt.Errorf("LooksLike matcher expects a string")
	}
	return dedent(matcher.expected) == dedent(given), nil
}

func (matcher *lookLikeMatcher) FailureMessage(actual interface{}) (message string) {
	if given, ok := actual.(string); ok {
		return fmt.Sprintf("Expected\n%s\nto look like\n%s", dedent(given), matcher.expected)
	}
	return fmt.Sprintf("Expected\n%#v\nto look like\n%s", actual, matcher.expected)
}

func (matcher *lookLikeMatcher) NegatedFailureMessage(actual interface{}) (message string) {
	if given, ok := actual.(string); ok {
		return fmt.Sprintf("Expected\n%s\nnot to look like\n%s", dedent(given), matcher.expected)
	}
	return fmt.Sprintf("Expected\n%#v\nnot to look like\n%s", actual, matcher.expected)
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
	if shortestIndent == 0 {
		return s
	}
	result := []string{}
	for _, line := range lines[firstLineWithText : lastLineWithText+1] {
		start := shortestIndent
		if start > len(line) {
			start = len(line)
		}
		result = append(result, line[start:])
	}
	return strings.Join(result, "\n")
}
