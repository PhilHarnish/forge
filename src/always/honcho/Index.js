
var Index = function () {
  this._index = {};
  this._listeners = {};
};

Index.prototype = {
  add: function (resource, references) {
    references = references || resource.references;
    for (var reference in references) {
      // TODO: Support multiple adds?
      this._index[reference] = resource;
    }
    if (!(resource.id in this._listeners)) {
      var listener = function () {
        this.add.apply(this, arguments);
      };
      this._listeners[resource.id] = listener;
      resource.onReferencesAdded(listener);
    }
  },

  remove: function (resource) {
    var references = resource.references;
    for (var reference in references) {
      delete this._index[reference];
    }
    resource.onReferencesAdded.remove(this._listeners[resource.id]);
  },

  find: function (reference) {
    return this._index[reference];
  }
};

module.exports = Index;


