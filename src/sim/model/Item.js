angular.module('sim/db/Item.js', ['sim/db/MongolabEndpoint.js']).
    factory('Item', function(MongolabEndpoint) {
      return MongolabEndpoint('sim-items/:id');
    });
