angular.module("sim/model/Action.js", []).
    factory("Action", function() {
      function Action(name, disabled) {
        this.name = name;
        this.disabled = disabled;
      }
      return Action;
    });
