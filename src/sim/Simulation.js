angular.module("sim/Simulation.js", [
      "sim/model/Item.js",
      "sim/model/Location.js",
      "sim/model/MongolabEndpoint.js",
      "sim/model/Player.js",
      "sim/ui/ActionBar.js",
      "sim/ui/Explore.js",
      "sim/ui/Rest.js",
      "sim/ui/Status.js"
    ]).
    factory("Simulation", function() {
      return Simulation;
    });

// TODO(philharnish): Wrap object to avoid window pollution.
// TODO(philharnish): See ngViewDirective for scope $destroy and creation
// pattern.
function Simulation($scope, $location, Item, Location, MongolabEndpoint, Player,
    Status) {
  MongolabEndpoint.$scope = $scope;
  $scope.tabs = ["explore", "rest"];
  $scope.items = Item.query();
  $scope.locations = Location.query();
  $scope.player = Player.get({id: "50b6f69be4b0dbae32c8ece1"});
  $scope.$watch(
      function () {
        // Requires closure since $location.path must not take arguments
        // and we'd rather have the last piece of the path regardless.
        return $location.path().split("/").pop();
      },
      function (path) {
        // Requires closure since setMode is not bound to player.
        $scope.player.setMode(path);
      });
}
