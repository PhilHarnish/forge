angular.module('sim/model/Location.js', ['sim/model/MongolabEndpoint.js']).
    factory('Location', function(MongolabEndpoint) {
      var Location = MongolabEndpoint('sim-locations/:id');

      Location.prototype.direction = function (source) {
        var altitude = this.z - source.z;
        var deltaX = this.x - source.x;
        var deltaY = this.y - source.y;
        var distance = Math.abs(deltaX) + Math.abs(deltaY);
        var rotation = distance ? Math.atan2(deltaY, deltaX) : 0;
        return {
          altitude: altitude,
          distance: distance,
          rotation: rotation
        };
      };

      return Location;
    });
