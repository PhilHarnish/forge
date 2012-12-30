angular.module('sim/model/Location.js', ['sim/model/MongolabEndpoint.js']).
    factory('Location', function(MongolabEndpoint) {
      var Location = MongolabEndpoint('sim-locations/:id');

      Location.prototype.direction = function(source) {
        return direction(this.x, this.y, this.z, source.x, source.y, source.z);
      };

      Location.prototype.distance = function(source) {
        return direction(this.x, this.y, this.z, source.x, source.y, source.z).
            distance;
      };

      Location.prototype.id = function() {
        return this._id.$oid;
      };

      // TODO(philharnish): Test cache.
      var directionCache = {};
      var directionCacheList = [];
      var MAX_DIRECTION_CACHE = 200;

      function direction(x1, y1, z1, x2, y2, z2) {
        var cacheKey = [x1, y1, z1, x2, y2, z2].join(",");
        if (!(cacheKey in directionCache)) {
          var deltaX = x1 - x2;
          var deltaY = y1 - y2;
          var distance = Math.abs(deltaX) + Math.abs(deltaY);
          var rotation = distance ? Math.atan2(deltaY, deltaX) : 0;
          directionCache[cacheKey] = {
            altitude: z1 - z2,
            distance: distance,
            rotation: rotation
          };
          directionCacheList.push(cacheKey);
          while (directionCacheList.length > MAX_DIRECTION_CACHE) {
            delete directionCache[directionCacheList.shift()];
          }
        }
        return directionCache[cacheKey];
      }

      return Location;
    });
