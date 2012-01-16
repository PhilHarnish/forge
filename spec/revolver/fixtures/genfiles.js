var fs = require("fs"),
    sys = require("sys"),

    fixtures = require("./index.js");

var _openDirs = {};

exports.setup = function (deps) {
  var root = __dirname + "/" + "tmp_" + Math.random().toString().slice(2);
  var createdDirectories = {};
  var addedDirs = [];
  var addedFiles = [];
  for (var fileName in deps) {
    var pathParts = fileName.split("/");
    pathParts.unshift(root);
    for (var i = 1; i < pathParts.length; i++) {
      var dirName = pathParts.slice(0, i).join("/");
      if (!(dirName in createdDirectories)) {
        createdDirectories[dirName] = true;
        fs.mkdirSync(dirName, "744");
        addedDirs.push(dirName);
      }
    }
    fs.writeFileSync(root + "/" + fileName, fixtures.getFileContents(fileName));
    addedFiles.push(root + "/" + fileName);
  }
  _openDirs[root] = {
    files: addedFiles,
    dirs: addedDirs
  };
  return root;
};

exports.cleanup = function () {
  for (var dirName in _openDirs) {
    var dir = _openDirs[dirName];
    var addedFiles = dir.files;
    var addedDirs = dir.dirs;
    var path;
    while (addedFiles.length) {
      path = addedFiles.pop();
      if (path.indexOf(__dirname + "/") == 0) {
        fs.unlinkSync(path);
      } else {
        console.log("ERROR: Attempted to remove", path);
      }
    }
    while (addedDirs.length) {
      path = addedDirs.pop();
      if (path.indexOf(__dirname + "/") == 0) {
        fs.rmdirSync(path);
      } else {
        console.log("ERROR: Attempted to remove", path);
      }
    }
  }
};
