// TODO(philharnish): Reusable library.
angular.module('location', ['ngResource']).
    factory('Location', function($resource) {
      var Location = $resource('https://api.mongolab.com/api/1/databases' +
          '/philharnish/collections/sim-locations/:id',
          {
            apiKey: '50b6e5c8e4b01e3a4a9cb693'
          },
          {
            update: { method: 'PUT' }
          }
      );

      Location.prototype.distance = function () {
        return this.x + this.y + this.z;
      };

      Location.prototype.cssRotation = function () {
        var rotation = 33 * (this.x + this.y + this.z);
        return {
          "-webkit-transform": "rotate(" + rotation + "deg)",
          "-moz-transform": "rotate(" + rotation + "deg)",
          "transform": "rotate(" + rotation + "deg)"
        };
      };

      Location.prototype.update = function(cb) {
        return Location.update({id: this._id.$oid},
            angular.extend({}, this, {_id:undefined}), cb);
      };

      return Location;
    });
