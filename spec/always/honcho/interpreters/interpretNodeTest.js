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
    var resource = {
      fileName: fileName,
      contents: fixtures.getFileContents(fileName)
    };
    var result = interpreter(resource);
    expect(result.deps).toEqual(fixtures.getDeps(fileName)[fileName]);
  });

  it("should identify all fixture dependencies.", function () {
    var expected = fixtures.getDeps();
    var actual = {};
    for (var fileName in expected) {
      var resource = {
        fileName: fileName,
        contents: fixtures.getFileContents(fileName)
      };
      actual[fileName] = interpreter(resource).deps;
    }
    expect(actual).toEqual(expected);
  });
});
