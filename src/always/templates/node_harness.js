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
