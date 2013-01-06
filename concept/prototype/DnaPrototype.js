angular.module("DnaPrototype.js", []).
    controller("DnaPrototype", DnaPrototype);

function DnaPrototype($scope, $location) {
  $scope.tabs = ["YAML", "Value", "Encoding"];
  $scope.mode = "Value";
  $scope.$watch(
      function() {
        // Wait until player is initialized before setting the mode.
        return $location.path().split("/").pop();
      },
      function(path) {
        if (path) {
          $scope.mode = path;
        }
      });
}
