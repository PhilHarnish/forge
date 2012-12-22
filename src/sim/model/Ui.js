angular.module("sim/model/Ui.js", [
      "sim/model/Mode.js"
    ]).
    factory("Ui", function(Mode) {
      function Ui(data) {
        this.update(data || {});
      }
      Ui.prototype.update = function (data) {
        this.data = data;
        this.modes = {};
         // Replace each mode with a Mode instance.
        for (var key in data.modes) {
          this.modes[key] = new Mode(key, data.modes[key]);
        }
      };
      Ui.prototype.mode = function (mode) {
        if (mode !== undefined) {
          this.data.mode = mode;
        }
        return this.data.mode;
      };
      return Ui;
    });
