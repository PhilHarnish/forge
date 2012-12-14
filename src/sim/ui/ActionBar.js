angular.module("sim/ui/ActionBar.js", []).
    factory("ActionBar", function() {
      return ActionBar;
    });

angular.module("sim/Simulation.js").
    directive("actionbar", function () {
      return {
        restrict: "E",
        templateUrl: "ui/ActionBar.html"
      }
    });

// TODO(philharnish): Wrap object to avoid window pollution.
function ActionBar() {
}
