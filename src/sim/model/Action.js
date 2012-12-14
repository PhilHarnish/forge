angular.module("sim/model/Action.js", []).
    factory("Action", function() {
      function Action(name, active, disabled) {
        this.name = name;
        this.active_ = active;
        this.disabled = disabled;
      }
      Action.prototype.active = function (activate) {
        if (activate !== undefined) {
          this.active_ = activate;
        }
        return this.active_;
      };
      return Action;
    });
