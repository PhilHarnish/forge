var spec = require("../../../../test"),

    fixtures = require("spec/revolver/fixtures"),
    interpretNode = require("src/always/honcho/interpreters/interpretNode.js");

var interpreter;
for (var k in interpretNode) {
  interpreter = interpretNode[k];
  break;
}
describe("Identifies dependencies", function () {
  it("should identify dependencies for a single file", function () {
    var fileName = "events/EventDispatcher.js";
    var result = interpreter(fileName, fixtures.getFileContents(fileName));
    expect(result.deps).toEqual(fixtures.getDeps(fileName)[fileName]);
  });

  it("should identify all fixture dependencies.", function () {
    var expected = fixtures.getDeps();
    var actual = {};
    for (var fileName in expected) {
      actual[fileName] = interpreter(fileName,
          fixtures.getFileContents(fileName)).deps;
    }
    expect(expected).toEqual(actual);
  });
});
