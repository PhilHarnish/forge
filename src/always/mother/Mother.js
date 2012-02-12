var fs = require("fs"),

    Index = require("always/mother/Index.js"),
    interpret = require("always/mother/interpret.js"),
    Resource = require("always/mother/Resource.js"),
    revolver = require("revolver/revolver.js"),
    Signal = require("signal/Signal.js");

var Mother = function () {
  this._index = new Index();
  this._affected = {};
  this.onFileChange = new Signal();
};

var FILE_ID_REGEX = /(?:(?:[^/]+\/)*..?\/)*(.*)$/;

Mother.prototype = {
  load: function (fileName) {
    var resource = this.resolve(fileName);
    if (!resource.contents && !resource.writeLock) {
      resource.writeLock = true;
      this._getFileContents(resource.fileName, function (err, data) {
        resource.writeLock = false;
        resource.setContents(data.toString());
      });
    }
  },

  loadDir: function (dirName) {
    var that = this;
    fs.readdir(dirName, function (err, files) {
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        if (file != "third_party" && file[0] != ".") {
          that._loadRecursive(dirName + "/" + file);
        }
      }
    });
  },

  _loadRecursive: function (path) {
    var that = this;
    fs.stat(path, function (err, stats) {
      if (stats.isDirectory()) {
        that.loadDir(path);
      } else {
        that.load(path);
      }
    });
  },

  find: function (reference) {
    return this._index.find(reference);
  },

  resolve: function (fileName) {
    // Remove "../" from fileName.
    fileName = FILE_ID_REGEX.exec(fileName)[1];
    var result = this.find(fileName);
    if (!result) {
      result = Resource.fromFileName(fileName);
      result.onContentsChanged(this, this._onContentsChanged);
      var that = this;
      result.onStatsChanged(function (curr, prev) {
        that._onStatsChanged(result, curr, prev);
      });
      this._index.add(result);
    } else if (result.fileName != fileName) {
      result.rename(fileName);
    }
    if (fileName[0] == "/") {
      // TODO: Handle renames.
      fs.watchFile(fileName, result.onStatsChanged);
    }
    return result;
  },

  test: function (path) {
    var tests = {};
    // TODO: Hacky! Find a better way to get all tests.
    for (var key in this._index._index) {
      var resource = this._index._index[key];
      if (!(resource.id in tests) && resource.type && resource.type.test) {
        tests[resource.id] = resource;
        try {
          require(resource.fileName);
        } catch (e) {
          console.log(e.stack);
        }
      }
    }
  },

  getAffected: function (resource) {
    return visitAffected(this._affected, this._index, resource, {});
  },

  _getFileContents: fs.readFile,

  _onContentsChanged: function (resource, contents) {
    resource.type = interpret.identify(resource);
    var interpretation = interpret.interpret(resource),
        i,
        dep;
    if (resource.deps) {
      // Remove old deps.
      for (i = 0; i < resource.deps.length; i++) {
        dep = this.resolve(resource.deps[i]);
        if (dep.id in this._affected) {
          delete this._affected[dep.id][resource.id];
        }
      }
    }
    resource.deps = interpretation.deps;
    if (resource.deps) {
      for (i = 0; i < resource.deps.length; i++) {
        dep = this.resolve(resource.deps[i]);
        if (!(dep.id in this._affected)) {
          this._affected[dep.id] = {};
        }
        this._affected[dep.id][resource.id] = resource;
      }
    }
  },

  _onStatsChanged: function (resource, curr, prev) {
    var diff = {},
        same = true,
        key;
    for (key in curr) {
      if (key != "atime" && curr[key].toString() != prev[key].toString()) {
        diff[key] = curr[key];
        same = false;
      }
    } 
    for (key in prev) {
      if (key != "atime" && curr[key].toString() != prev[key].toString()) {
        diff[key] = prev[key];
        same = false;
      }
    }
    if (!same) {
      // TODO: This seems like an awkward place to unload resources.
      var affected = this.getAffected(resource);
      for (var f in affected) {
        revolver.unload(affected[f].fileName);
      }
      this.onFileChange(affected);
    }
  }
};

function visitAffected(affectedMap, index, resource, result) {
  if (!(resource.id in result)) {
    result[resource.id] = resource;
    var affected = affectedMap[resource.id];
    for (var resourceId in affected) {
      visitAffected(affectedMap, index, index.find(resourceId), result);
    } 
  }
  return result;
}

module.exports = Mother;
