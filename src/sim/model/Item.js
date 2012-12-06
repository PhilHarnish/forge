angular.module('model/Item.js', ['model/MongolabEndpoint.js']).
    factory('Item', function(MongolabEndpoint) {
      return MongolabEndpoint('sim-items/:id');
    });
