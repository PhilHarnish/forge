angular.module('sim/model/Item.js', ['sim/model/MongolabEndpoint.js']).
    factory('Item', function(MongolabEndpoint) {
      return MongolabEndpoint('sim-items/:id');
    });
