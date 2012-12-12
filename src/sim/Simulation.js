angular.module("sim/Simulation.js", [
    "sim/model/Item.js",
    "sim/model/Location.js",
    "sim/model/MongolabEndpoint.js",
    "sim/model/Player.js",
    "sim/ui/Status.js"]).
    factory("Simulation", function() {
      return Simulation;
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function Simulation($scope, $location, Item, Location, MongolabEndpoint, Player, Status) {
  MongolabEndpoint.$scope = $scope;
  $scope.tabs = ["explore", "rest"];
  $scope.items = Item.query();
  $scope.locations = Location.query();
  $scope.player = Player.get({id: "50b6f69be4b0dbae32c8ece1"});
  $scope.status = new Status();
  $scope.$watch("player.stats", function () {
    if ($scope.player.initialized()) {
      $scope.status.set($scope.player.stats);
    }
  });
}
