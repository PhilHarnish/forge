var _ = require("third_party/underscore/underscore.js"),
    Dna = require("src/dna/Dna.js");

describe("dna", function() {
  it("should default to a string with zero", function() {
    var d = new Dna();
    expect(d.toString()).toEqual(String.fromCharCode(0));
  });

  it("should handle '0' characters in the middle.", function() {
    var d = new Dna(String.fromCharCode(72,
        0, 69,
        0, 76, 0, 76,
        0, 79, 0, 0, 0, 0, 0, 0));
    expect(d.toString().split(String.fromCharCode(0)).join('')).
        toEqual("HELLO");
  });

  it("should throw an error if initialized with invalid length", function () {
    _([2, 5, 11, 21]).each(function(length) {
      var input = String.fromCharCode.apply(String, _.range(length));
      expect(function () { var d = new Dna(input); }).
          toThrow(jasmine.any(RangeError));
    });
  });
});
