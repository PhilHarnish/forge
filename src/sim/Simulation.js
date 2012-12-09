angular.module('sim/Simulation.js', ['sim/model/Item.js', 'sim/model/Location.js', 'sim/model/Player.js']).
  factory('Simulation', function() {
      return Simulation;
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function Simulation($scope, Item, Location, Player) {
  $scope.items = Item.query();
  $scope.locations = Location.query();
  $scope.player = Player.get({id: "50b6f69be4b0dbae32c8ece1"});
}
