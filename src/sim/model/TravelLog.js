angular.module("sim/model/TravelLog.js", [
      "sim/model/Location.js"
    ]).
    factory("TravelLog", function(Location) {
      // TODO(philharnish): Restrict inventory by player ID.
      function TravelLog(id) {
        this.locations = Location.query();
      }
      return TravelLog;
    });
