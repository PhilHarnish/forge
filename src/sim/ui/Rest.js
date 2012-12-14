angular.module("sim/ui/Rest.js", []).
    factory("Rest", function() {
      return Rest;
    });

angular.module("sim/Simulation.js").
    directive("rest", function () {
      return {
        restrict: "E",
        scope: {
          player: "="
        },
        templateUrl: "ui/Rest.html"
      }
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function Rest() {
}
