angular.module("DnaPrototype.js", []).
    controller("DnaPrototype", DnaPrototype);

function DnaPrototype($scope, $location) {
  $scope.tabs = ["yaml", "value", "encoding"];
  $scope.data = {
    "yaml": "",
    "value": [1, 1, 1, 1, 1, 1].join("\n"),
    "encoding": ""
  };
  $scope.encoding = "";
  $scope.$watch(
      function() {
        // Wait until player is initialized before setting the mode.
        return $location.path().split("/").pop();
      },
      function(path) {
        if (!path || !(path in $scope.data)) {
          $location.path("/value");
        } else {
          update($scope.mode, path, $scope.data);
          $scope.mode = path;
        }
      });
}

function update(last, next, scope) {
  //
}
