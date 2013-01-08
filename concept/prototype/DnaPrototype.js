angular.module("DnaPrototype.js", [
      "DnaEncoder.js"
    ]).
    controller("DnaPrototype", DnaPrototype);

function DnaPrototype($scope, $location, DnaEncoder) {
  $scope.tabs = ["model", "value", "encoding"];
  $scope.data = {
    "model": "",
    "value": [1, 1, 1, 1, 1, 1].join("\n"),
    "encoding": ""
  };
  var encoder = new DnaEncoder();
  $scope.$watch(
      function() {
        // Wait until player is initialized before setting the mode.
        return $location.path().split("/").pop();
      },
      function(path) {
        if (!path || !(path in $scope.data)) {
          $location.path("/value");
        } else {
          if ($scope.mode == "value") {
            encoder.setValue($scope.data.value);
            $scope.data.value = encoder.getValue();
            $scope.data.encoding = encoder.getEncoding();
          } else if ($scope.mode == "model") {
            encoder.setModel($scope.data.model);
            $scope.data.encoding = encoder.getEncoding();
          }
          $scope.mode = path;
        }
      });
}
