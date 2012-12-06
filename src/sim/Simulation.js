angular.module('Simulation.js', ['model/Item.js']).
  factory('Simulation', function() {
      console.log("Factory method called.");
      return Simulation;
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function Simulation($scope, Item) {
  $scope.items = Item.query();
  $scope.message = "Hello world.";
}
