exports = {};
module = {
  exports: exports
};
deps = {};
function require(path) {
  if (!(path in deps)) {
    deps[path] = {};
  }
  return deps[path];
}

// TODO: This kinda sucks. Needed for node's event.js
process = {
  EventEmitter: function () {}
};
