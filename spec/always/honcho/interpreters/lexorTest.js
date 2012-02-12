var spec = require("../../../../test"),
    lexor = require("always/mother/interpreters/lexor.js");

var START,
    result;

START = new lexor.State("START");
LOWER_ALPHA = new lexor.State("LOWER_ALPHA");
UPPER_ALPHA = new lexor.State("UPPER_ALPHA");
START.on(/[a-z]+/, LOWER_ALPHA, START);
START.on(/[A-Z]+/, UPPER_ALPHA, START);

var lexer = new lexor.Lexer(START);

var LIPSUM = [
    "Lorem ipsum dolor sit amet, consectetur adipisicing elit,",
    " sed do eiusmod tempor incididunt ut labore et dolore magna",
    " aliqua. Ut enim ad minim veniam, quis nostrud exercitation",
    " ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    " Duis aute irure dolor in reprehenderit in voluptate velit",
    " esse cillum dolore eu fugiat nulla pariatur. Excepteur sint",
    " occaecat cupidatat non proident, sunt in culpa qui officia",
    " deserunt mollit anim id est laborum."
];

var JAVA_SCRIPT = [];
for (var fn in jasmine) {
  if (typeof jasmine[fn] == "function") {
    JAVA_SCRIPT.push("var " + fn + " = ");
    JAVA_SCRIPT.push(jasmine[fn].toString());
    JAVA_SCRIPT.push(";");
  }
}

var PYTHON_SRC = [
    "def fib(n):\n",
    "  if n == 0:\n",
    "    return 0\n",
    "  elif n == 1:\n",
    "    return 1\n",
    "  else:\n",
    "    return fib(n - 1) + fib(n - 2)\n"
];

// TODO: Assume return to initial state if no transitions defined.
var PYTHON = new lexor.State("PYTHON", false);
PYTHON.BEGIN_EXPRESSION = new lexor.State("BEGIN_EXPRESSION");
PYTHON.OPERATOR = new lexor.State("OPERATOR");
PYTHON.KEYWORD = new lexor.State("KEYWORD");
PYTHON.IDENTIFIER = new lexor.State("IDENTIFIER");
PYTHON.DIGIT = new lexor.State("DIGIT");
PYTHON.WHITESPACE = new lexor.State("WHITESPACE");
PYTHON.NEWLINE = new lexor.State("NEWLINE");
PYTHON.INDENT = new lexor.State("INDENT");
PYTHON.DEDENT = new lexor.State("DEDENT");
PYTHON.handleIndent = (function () {
  var depth = 0;
  var levels;
  return function (string, matchStart, matchEnd) {
    var result = [];
    var indent = matchEnd - matchStart;
    if (!levels) {
      levels = [indent];
    } else if (indent == levels[depth]) {
      result.push(PYTHON.BEGIN_EXPRESSION);
    } else if (indent > levels[depth]) {
      result.push(PYTHON.INDENT);
      depth++;
      levels[depth] = indent;
    } else if (depth > 0) {
      result.push(PYTHON.DEDENT);
      depth--;
    }
    result.push(PYTHON.WHITESPACE);
    // Attribute indent width to preceding token. (Make this default?)
    result.push(matchEnd);
    return result;
  };
})();

PYTHON.NEWLINE.on(/^\s*/, PYTHON.handleIndent, PYTHON);

PYTHON.on(/^\n/, PYTHON.NEWLINE);
PYTHON.on(/^\s+/, PYTHON.WHITESPACE, PYTHON);
PYTHON.on(/^(def|if|elif|else|return)/, PYTHON.KEYWORD, PYTHON);
PYTHON.on(/^[a-z]+/, PYTHON.IDENTIFIER, PYTHON);
PYTHON.on(/^[0-9]/, PYTHON.DIGIT, PYTHON);
PYTHON.on(/^([-+=:]+|[()])/, PYTHON.OPERATOR, PYTHON);

lexer = new lexor.Lexer(PYTHON.NEWLINE);
lexer.update(PYTHON_SRC.join(""));
var max = 100;
var tokens = [];
do {
  var token = lexer.getNextToken();
  tokens.push(token);
} while (token && max--);

describe("States", function () {
  it("should transition states", function () {
  });
});

xdescribe("Lexing", function () {
  beforeEach(function () {
    START = new lexor.State();
  });

  it("lexer without states returns input", function () {
    START = new lexor.State();
    result = START.update("Unlexable input.");
    expect(result.remaining).toBe("Unlexable input.");
  });
});
