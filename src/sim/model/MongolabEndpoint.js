angular.module('sim/db/MongolabEndpoint.js', ['ngResource']).
    factory('MongolabEndpoint', function($resource) {
      var MongolabEndpoint = function (path) {
        var Klass = $resource(MongolabEndpoint.BASE_URL + path,
            MongolabEndpoint.DEFAULTS,
            MongolabEndpoint.ACTIONS);
        Klass.prototype.update = function(cb) {
          return Klass.update({id: this._id.$oid},
              angular.extend({}, this, {_id:undefined}), cb);
        };
        return Klass;
      };
      MongolabEndpoint.BASE_URL =
          'https://api.mongolab.com/api/1/databases' +
              '/philharnish/collections/';
      MongolabEndpoint.DEFAULTS = {
        apiKey: '50b6e5c8e4b01e3a4a9cb693'
      };
      MongolabEndpoint.ACTIONS = {
        update: {
          method: 'PUT'
        }
      };

      return MongolabEndpoint;
    });
