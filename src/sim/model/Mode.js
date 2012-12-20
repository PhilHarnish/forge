angular.module("sim/model/Mode.js", []).
    factory("Mode", function() {
      return Mode;
    });

function Mode(name, model) {
  this.activity = model.activity;
}
Mode.prototype.parseActionList = function (list) {
  var actions = [];
  for (var i = 0; i < list.length; i++) {
    var action = list[i];
    actions.push({
      name: action.name,
      active: activeFn(this, action.name),
      enabled: enabledFn(action)
    });
  }
  return actions;

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
