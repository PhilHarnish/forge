angular.module('sim/ui/Status.js', []).
    factory('Status', function() {
      var STAT_CSS = {
        health: "info",
        hunger: "success",
        energy: "warning"
      };
      var Status = function(stats) {
        this.set(stats);
      };
      Status.prototype.set = function(stats) {
        this.stats = stats;
      };
      Status.prototype.progressClass = function(stat) {
        return "progress progress-" + STAT_CSS[stat];
      };
      return Status;
    });
