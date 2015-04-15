angular.module("sim/Simulation.js", [
      "sim/model/Player.js",
      "sim/ui/ActionBar.js",
      "sim/ui/Explore.js",
      "sim/ui/Rest.js",
      "sim/ui/Status.js"
    ]).
    controller("Simulation", Simulation);

function Simulation($scope, $location, Player) {
  // TODO(philharnish): See ngViewDirective for scope $destroy and
  // creation pattern.
  $scope.tabs = ["explore", "rest"];
  $scope.player = new Player("50b6f69be4b0dbae32c8ece1");
  $scope.$watch(
      function() {
        // Wait until player is initialized before setting the mode.
        return $scope.player.initialized() &&
            $location.path().split("/").pop();
      },
      function(path) {
        if (path) {
          $scope.player.ui.mode(path);
        }
      });
}
