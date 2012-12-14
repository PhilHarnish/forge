angular.module("sim/ui/Status.js", []).
    factory("Status", function() {
      return Status;
    });

angular.module("sim/Simulation.js").
    directive("status", function () {
      return {
        restrict: "E",
        scope: {
          stats: "="
        },
        templateUrl: "ui/Status.html"
      }
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function Status($scope) {
  var STAT_CSS = {
    health: "info",
    hunger: "success",
    energy: "warning"
  };
  $scope.progressClass = function(stat) {
    return "progress progress-" + STAT_CSS[stat];
  };
}
