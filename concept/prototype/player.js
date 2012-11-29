angular.module('player', ['ngResource']).
    factory('Player', function($resource) {
      var Player = $resource('https://api.mongolab.com/api/1/databases' +
          '/philharnish/collections/sim-players/:id',
          { apiKey: '50b6e5c8e4b01e3a4a9cb693' }, {
            update: { method: 'PUT' }
          }
      );

      Player.prototype.update = function(cb) {
        return Player.update({id: this._id.$oid},
            angular.extend({}, this, {_id:undefined}), cb);
      };

      return Player;
    });
