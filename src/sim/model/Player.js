angular.module('sim/model/Player.js', [
      'sim/model/Inventory.js',
      'sim/model/Item.js',
      'sim/model/MongolabEndpoint.js',
      'sim/model/Ui.js'
    ]).
    factory('Player', function(Inventory, Item, MongolabEndpoint, Ui) {
      var Player = MongolabEndpoint('sim-players/:id');
      var getFn = Player.get;
      Player.get = function(parameters) {
        return getFn(parameters, onSuccess);
      };

      Player.prototype.initialized = function() {
        return !!this._id;
      };

      Player.prototype.onSuccess = function() {
        // Convert `this` to services.
        this.inventory = new Inventory(Item.query());
        this.ui = new Ui(this.ui);
      };

      Player.prototype.modeIs = function(mode) {
        return this.initialized() && this.ui.mode == mode;
      };

      Player.prototype.setMode = function(mode) {
        return this.initialized() && this.ui.setMode(mode);
      };

      return Player;

      function onSuccess(value, headers) {
        value.onSuccess();
      }
    });
