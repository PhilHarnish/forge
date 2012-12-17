angular.module("sim/model/Mode.js", []).
    factory("Mode", function() {
      return Mode;
    });

function Mode() {
}
Mode.prototype.parseActionList = function (list) {
  var actions = [];
  for (var i = 0; i < list.length; i++) {
    var action = list[i];
    actions.push({
      name: action,
      active: bind(this, action, "Active"),
      enabled: bind(this, action, "Enabled")
    });
  }
  return actions;

  function bind(self, action, key) {
    var name = action + key;
    return function () {
      if (angular.isFunction(self[name])) {
        return self[name].apply(self, arguments);
      }
      return self[name] === undefined ?
          true : self[name];
    };
  }
};

