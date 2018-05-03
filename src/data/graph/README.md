# Syntax
## Standard RegEx
* Fixed length: Only accept words of specified length.
  * Implemented in regex with fixed length expressions: `/....../`
* Variable length: Ability to match entire corpus.
  * Implemented in regex using Kleene star: `/.*/`
  * Results are weighted by frequency.
* Multi-word: Ability to match more than one word.
  * Implemented in regex using space: `/.* .*/`
  * Results are weighted by n-gram frequency.
* Starting characters: Characters required to be matched.
  * Implemented in regex as `/some prefix.*/`
* Branching paths: Characters must match one (and only one) of several options.
  * Implemented in regex as `/a|b|(c|d)/`
* Provided characters: Characters assumed to be already returned.
  * Out of scope?
* Input streams: Ability to accept variable input.
  * Implemented in regex using group reference syntax: `/a\g<name>b`
* Output streams: Ability to forward subtext on to further expressions.
  * Implemented in regex with capture groups: `/a(.*)b/`
  * Or, optionally named capture groups: `/a(?P<group_name>.*)b/`

## Novel
Additional expressiveness is borrowed or inspired by Qat.

### Composition
Chaining expressions can further refine results. This is implemented similar to
Qat's `|` and `&` operators. `|` has the same RegEx and Qat semantics (above)
while `&` behaves like Qat, as far as I can tell.

These expressions are evaluated in parallel. Any input or output streams will
constrain each other. That is, if a specific input value is chosen then it will
be assumed by the other and vice-versa.

### Mutations
Off-by-N changes with optional edit weights.

### Reversal
Reversing an input can be done with `~`, just like Qat: `/\<~input>/`

### Anagrams
Consume some or all of a set of characters. Comparisons to Qat:
* `/anagram` is `/{anagram}/`
* `/anagram*` is `/{anagram.*}/`
* `/anagram.` is `/{anagram.}/`
* `3-:*/anagram` is `/{anagram}{3,}/`
* `3-5:*/anagram` is `/{anagram}{3,5}/`

As well as impossible Qat expressions.
* Anagram of multiple variable inputs: restricts solutions to words produced by
  combinations of other input streams.
  * `/{\g<first>\g<second>}/`
* Anagram with multi-word outputs: include whitespace to determine output.
  * `/{monogamist }/` gives "moist mango", "mango moist", etc in frequency order
  * `/{monogamist }&.... ......` gives "moon stigma", etc
* Anagrams of multi-character atoms: restricts solutions to combinations of
  comma-separated inputs.
  * `/{a,ab,abc}/` gives a, aba, abc, but not abac etc.
* Anagrams of specific choices: restricts solutions to one of some choices
  * `/{(a|b),(c|d),(e|f)/}` gives ace, fad, bed, etc

### Multiple expressions.
A semi-colon (`;`) can be used as shorthand for multiple expressions. Examples
comparing Qat and `;` separated expressions:
* `aAb;A` is `/a(?P<A>);\g<A>/`

# Traversal
Considerable state is maintained while walking the Trie:
* Lookahead.
  * If minimum or maximum word length is known it is used.
  * If required future characters are known they are used.
  * Required lookahead can be ORed or ANDed together.
* Snapshots. Traversal is done using a method similar to A*. Many cursors must
  be held in memory during traversal which lends itself to pooling objects which
  must be requested and explicitly freed.

# Algebra
A node can be expanded to other nodes including itself.
Traversing a parent node may involve simultaneous traversal of inner nodes.

# TODO
## Usability
* Convenience methods

## Graph traversal
* Edits
   * Adding nodes
   * Subtracting nodes
* % traversed

## Dictionary
* Load dictionary based on length and prefixes

## Regex
* `a&b` simultaneous expressions
* `a;b` parallel expressions
* `ABA;AB;B` variable expressions
* `{anagram}{x,y}` and `{anagram}{x-y}`

## Optimizations
* Start with trie matching required lengths?
* Merge regular expressions?
