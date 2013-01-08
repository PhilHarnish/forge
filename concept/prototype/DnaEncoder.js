angular.module("DnaEncoder.js", []).
    factory("DnaEncoder", function() {
      function DnaEncoder() {
      }

      DnaEncoder.prototype.setModel = function (model) {
        this.model = model;
      };

      DnaEncoder.prototype.setValue = function (value) {
        this.value = value;
      };

      DnaEncoder.prototype.getEncoding = function () {
        return this.value + "Encoded!";
      };

      return DnaEncoder;
    });
