var _NODE_REQUIRE_REGEXP = /\s*=\s*require\(/g;
var _NODE_ANGULAR_REGISTER_REGEXP = /register\(/g;
var _ANGULAR_REGEXP = /angular.module\(/g;

var _detectJavaScript = function (fileName,contents, type) {
  // TODO: Detect JavaScript.
  return null;
};

var _identifyJavaScript = function (fileName, contents, type) {
  if (contents.match(_NODE_REQUIRE_REGEXP)) {
    type += ";nodejs=1";
    if (contents.match(_NODE_ANGULAR_REGISTER_REGEXP)) {
      type += ";angularjs=1"
    }
  } else if (contents.match(_ANGULAR_REGEXP)) {
    type += ";angularjs=1";
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
