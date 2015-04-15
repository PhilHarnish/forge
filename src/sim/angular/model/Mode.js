angular.module("sim/model/Mode.js", []).
    factory("Mode", function() {
      return Mode;
    });

function Mode(name, model) {
  this.activity = model.activity;
}
Mode.prototype.parseActionList = function (list) {
  var actions = [];
  var map = {
    list: actions
  };
  for (var i = 0; i < list.length; i++) {
    var action = list[i];
    map[action.name] = {
      name: action.name,
      active: activeFn(this, action.name),
      enabled: enabledFn(action)
    };
    actions.push(map[action.name]);
  }
  return map;

  function activeFn(self, action) {
    return function (value) {
      if (value === true) {
        self.activity = action;
      }
      return self.activity == action;
    };
  }
  function enabledFn(activity) {
    return function () {
      return activity.enabled !== false;
    };
  }
};
