// TODO(philharnish): Reusable library.
angular.module('item', ['ngResource']).
    factory('Item', function($resource) {
      var Item = $resource('https://api.mongolab.com/api/1/databases' +
          '/philharnish/collections/sim-items/:id',
          {
            apiKey: '50b6e5c8e4b01e3a4a9cb693'
          },
          {
            update: { method: 'PUT' }
          }
      );

      Item.prototype.update = function(cb) {
        return Player.update({id: this._id.$oid},
            angular.extend({}, this, {_id:undefined}), cb);
      };

      return Item;
    });
