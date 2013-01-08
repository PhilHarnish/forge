angular.module("DnaPrototype.js", [
      "DnaEncoder.js"
    ]).
    controller("DnaPrototype", DnaPrototype);

function DnaPrototype($scope, $location, DnaEncoder) {
  $scope.tabs = ["yaml", "value", "encoding"];
  $scope.data = {
    "yaml": "",
    "value": [1, 1, 1, 1, 1, 1].join("\n"),
    "encoding": ""
  };
  $scope.encoder = new DnaEncoder();
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
            $scope.encoder.setValue($scope.data.value);
            $scope.data.encoding = $scope.encoder.getEncoding();
          } else if ($scope.mode == "yaml") {
            $scope.encoder.setModel($scope.data.yaml);
            $scope.data.encoding = $scope.encoder.getEncoding();
          }
          $scope.mode = path;
        }
      });
}
