angular.module('sim/ui/Status.js', []).
    factory('Status', function() {
      var Status = function (stats) {
        this.stats = stats;
      };
      Status.prototype.set = function (stats) {
        this.stats = stats;
      };
      return Status;
    });
