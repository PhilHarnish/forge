exports.unloadAll = function () {
  // Consider clearing path cache as well. This can be reached with:
  // require.cache[cache].constructor._pathCache.
  for (var cache in require.cache) {
    delete require.cache[cache];
  }
};

var _lastUnloadPrefix = "";
exports.unload = function (files) {
  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    if (_lastUnloadPrefix && ((_lastUnloadPrefix + file) in require.cache)) {
      delete require.cache[_lastUnloadPrefix + file];
    } else {
      for (var cache in require.cache) {
        var parts = cache.split(file);
        if (parts.length == 2 && parts[1] == "") {
          _lastUnloadPrefix = parts[0];
          delete require.cache[cache];
        }
      }
    }
  }
};

exports.getCacheList = function () {
  var result = [];
  for (var cache in require.cache) {
    result.push(cache);
  }
  return result;
};
