angular.module("sim/model/Ui.js", [
      "sim/model/Mode.js"
    ]).
    factory("Ui", function(Mode) {
      function Ui(model) {
        angular.copy(model, this);
        // Replace each mode with a Mode instance.
        for (var key in this.modes) {
          this.modes[key] = new Mode(key, this.modes[key]);
        }
      }
      Ui.prototype.setMode = function (mode) {
        this.mode = mode;
      };
      return Ui;
    });
