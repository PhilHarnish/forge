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
    controller("Simulation", Simulation);

function Simulation($scope, $location, Location, Player) {
  // TODO(philharnish): See ngViewDirective for scope $destroy and
  // creation pattern.
  $scope.tabs = ["explore", "rest"];
  $scope.locations = Location.query();
  $scope.player = new Player("50b6f69be4b0dbae32c8ece1");
  window.player = $scope.player;
  $scope.$watch(
      function () {
        // Requires closure since $location.path must not take arguments
        // and we'd rather have the last piece of the path regardless.
        return $location.path().split("/").pop();
      },
      function (path) {
        // Requires closure since setMode is not bound to player.
        $scope.player.mode(path);
      });
}
