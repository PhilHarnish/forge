_REQUIRE_REGEXP = /require\(['"]([^'"]+)['"]\)/g;

var _detectJavaScript = function (fileName,contents, type) {
  // TODO: Detect JavaScript.
  return null;
};

var _identifyJavaScript = function (fileName, contents, type) {
  // No reason to doubt type hint.
  return type;
};

module.exports = {
  "*": _detectJavaScript,
  "application/javascript": _identifyJavaScript
};
