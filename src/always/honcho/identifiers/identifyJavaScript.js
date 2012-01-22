var _REQUIRE_REGEXP = /\s*=\s*require\(/g;

var _detectJavaScript = function (fileName,contents, type) {
  // TODO: Detect JavaScript.
  return null;
};

var _identifyJavaScript = function (fileName, contents, type) {
  if (contents.match(_REQUIRE_REGEXP)) {
    type += ";nodejs=1";
  }
  if (fileName.slice(-7) == "Test.js") {
    type += ";test=1";
  }
  return type;
};

module.exports = {
  "*": _detectJavaScript,
  "application/javascript": _identifyJavaScript
};
