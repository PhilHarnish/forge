angular.module('sim/model/Player.js', [
      'sim/model/Inventory.js',
      'sim/model/MongolabEndpoint.js',
      'sim/model/TravelLog.js',
      'sim/model/Ui.js'
    ]).
    factory('Player', function(Inventory, MongolabEndpoint,
        TravelLog, Ui) {
      var PlayerEndpoint = MongolabEndpoint('sim-players/:id');
      var Player = function (id) {
        this.data = PlayerEndpoint.get({"id": id},
            angular.bind(this, this.onSuccess));
        this.inventory = new Inventory(id);
        this.travelLog = new TravelLog(id);
        this.ui = new Ui();
      };

      Player.prototype.initialized = function() {
        return !!this.data._id;
      };

      Player.prototype.onSuccess = function() {
        // Convert `this` to services.
        this.ui.update(this.data.ui);
      };

      Player.prototype.name = function () {
        return this.data.name;
      };

      Player.prototype.stats = function() {
        return this.data.stats;
      };

      return Player;
    });
