
angular.module('simulation', []).
  config(function($routeProvider) {
    $routeProvider.
      when('/explore', {
          controller: ExploreController,
          templateUrl: 'partials/explore.html'
      }).
      when('/rest', {
          controller: RestController,
          templateUrl: 'partials/rest.html'
      }).
      otherwise({redirectTo:'/explore'});
  }).
  directive('actionbar', function () {
      return {
        restrict: 'E',
        templateUrl: 'partials/action_bar.html'
      }
    });

function SimController($scope, $location) {
  $scope.modeIs = function(mode) {
    return $location.path() == '/' + mode;
  };
}

function MeterController($scope) {
  $scope.meters = [
    {
      name: "health",
      value: 20,
      css: "info"
    },
    {
      name: "hunger",
      value: 40,
      css: "success"
    },
    {
      name: "energy",
      value: 60,
      css: "warning"
    }
  ];
}

function ExploreController($scope) {
  $scope.actions = [
    {
      name: "fight",
      disabled: true,
      active: actionGetterSetter($scope)
    },
    {
      name: "flight",
      active: actionGetterSetter($scope)
    }
  ];
  $scope.action = $scope.actions[1];
  var distance = function () {
    return this.x + this.y + this.z;
  };
  var cssRotation = function () {
    var rotation = 33 * (this.x + this.y + this.z);
    return {
      "-webkit-transform": "rotate(" + rotation + "deg)",
      "-moz-transform": "rotate(" + rotation + "deg)",
      "transform": "rotate(" + rotation + "deg)"
    };
  };
  $scope.locations = [
    {
      name: "base",
      memorable: true,
      distance: distance,
      cssRotation: cssRotation,
      x: 0,
      y: 0,
      z: 0
    },
    {
      name: "locked door",
      memorable: true,
      distance: distance,
      cssRotation: cssRotation,
      x: 0,
      y: 10,
      z: 0
    },
    {
      name: "hostile",
      memorable: false,
      distance: distance,
      cssRotation: cssRotation,
      x: 10,
      y: 10,
      z: 0
    }
  ];
}

function RestController($scope) {
  $scope.actions = [
    {
      name: "fortify",
      active: actionGetterSetter($scope)
    },
    {
      name: "study",
      active: actionGetterSetter($scope)
    },
    {
      name: "sleep",
      active: actionGetterSetter($scope)
    }
  ];
  $scope.action = $scope.actions[0];
  $scope.items = [
    {
      name: "bat",
      owned: true,
      weight: 2
    },
    {
      name: "canned food",
      owned: true,
      weight: 3
    }
  ];
}

function actionGetterSetter($scope) {
  if (!$scope.hasOwnProperty("$actionGetterSetter")) {
    $scope.$actionGetterSetter =
        function (value) {
          if (value === undefined) {
            return $scope.action == this;
          } else if (this.disabled) {
            return;
          } else if (value) {
            $scope.action = this;
          }
          return value;
        };
  }
  return $scope.$actionGetterSetter;
}
