// TODO(philharnish): Reusable library.
angular.module('sim/model/Player.js', ['sim/model/MongolabEndpoint.js']).
    factory('Player', function(MongolabEndpoint) {
      var STAT_CSS = {
        health: "info",
        hunger: "success",
        energy: "warning"
      };
      var Player = MongolabEndpoint('sim-players/:id');

      Player.prototype.initialized = function() {
        return !!this._id;
      };

      return Player;
    });
