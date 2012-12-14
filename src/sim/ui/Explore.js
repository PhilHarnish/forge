angular.module("sim/ui/Explore.js", []).
    factory("Explore", function() {
      return Explore;
    });

angular.module("sim/Simulation.js").
    directive("explore", function () {
      return {
        restrict: "E",
        scope: {
          player: "="
        },
        templateUrl: "ui/Explore.html"
      }
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function Explore() {
}
