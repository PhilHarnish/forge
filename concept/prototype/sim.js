
angular.module('simulation', ['player']).
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

function SimController($scope, $location, Player) {
  $scope.player = Player.get({id: "50b6f69be4b0dbae32c8ece1"}, function (p) {
    if (p.name) {
      // Initialized.
      return;
    }
    p.name = "philharnish";
    p.ui = {
      mode: {
        explore: "flight",
        rest: "fortify"
      }
    };

    p.$save();
  });
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
      active: actionGetterSetter($scope, "explore")
    },
    {
      name: "flight",
      active: actionGetterSetter($scope, "explore")
    }
  ];
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
      active: actionGetterSetter($scope, "rest")
    },
    {
      name: "study",
      active: actionGetterSetter($scope, "rest")
    },
    {
      name: "sleep",
      active: actionGetterSetter($scope, "rest")
    }
  ];
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

function actionGetterSetter($scope, mode) {
  if (!$scope.hasOwnProperty("$actionGetterSetter")) {
    $scope.$actionGetterSetter =
        function (value) {
          if (value === undefined) {
            return $scope.player.ui &&
                $scope.player.ui.mode[mode] == this.name;
          } else if (this.disabled) {
            return;
          } else if (value) {
            $scope.action = this;
            $scope.player.ui.mode[mode] = this.name;
            $scope.player.update();
          }
          return value;
        };
  }
  return $scope.$actionGetterSetter;
}
