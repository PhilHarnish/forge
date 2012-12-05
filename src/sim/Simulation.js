angular.module('sim/Simulation.js', []).
  factory('Simulation', function() {
      console.log("Factory method called.");
      return Simulation;
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function Simulation($scope) {
  $scope.message = "Hello world.";
}
