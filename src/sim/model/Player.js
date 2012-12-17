angular.module('sim/model/Player.js', ['sim/model/MongolabEndpoint.js']).
    factory('Player', function(MongolabEndpoint) {
      var Player = MongolabEndpoint('sim-players/:id');

      Player.prototype.initialized = function() {
        return !!this._id;
      };

      Player.prototype.modeIs = function(mode) {
        return this.initialized() && this.ui.mode == mode;
      };

      Player.prototype.setMode = function(mode) {
        if (this.initialized()) {
          this.ui.mode = mode;
        }
      };

      Player.prototype.setActivity = function(activity) {
        if (this.initialized()) {
          this.ui.modes[this.ui.mode].activity = activity;
        }
      };

      Player.prototype.inventory = {
        "has": function () {
          return false;
        }
      };

      return Player;
    });
