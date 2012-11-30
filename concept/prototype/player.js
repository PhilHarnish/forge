// TODO(philharnish): Reusable library.
angular.module('player', ['ngResource']).
    factory('Player', function($resource) {
      var STAT_CSS = {
        health: "info",
        hunger: "success",
        energy: "warning"
      };
      var Player = $resource('https://api.mongolab.com/api/1/databases' +
          '/philharnish/collections/sim-players/:id',
          {
            apiKey: '50b6e5c8e4b01e3a4a9cb693'
          },
          {
            update: { method: 'PUT' }
          }
      );

      Player.prototype.initialized = function() {
        return !!this._id;
      };

      Player.prototype.update = function(cb) {
        return Player.update({id: this._id.$oid},
            angular.extend({}, this, {_id:undefined}), cb);
      };

      Player.prototype.statCss = function (stat) {
        return STAT_CSS[stat];
      };

      return Player;
    });
