angular.module('sim/Simulation.js', ['sim/model/Item.js']).
  factory('Simulation', function() {
      return Simulation;
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function Simulation($scope, Item) {
  $scope.items = Item.query();
  $scope.message = "Hello world.";
}
