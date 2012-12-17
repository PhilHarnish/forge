var MongolabFixture = require("./MongolabFixture.js");
var status = require("./status.js");
module.exports = MongolabFixture.exports("players", [
  {
    "_id": {
      "$oid": "50b6f69be4b0dbae32c8ece1"
    },
    "name": "philharnish",
    "stats": status.get(),
    "ui": {
      "mode": "rest",
      "modes": {
        "explore": {
          "activity": "flight"
        },
        "rest": {
          "activity": "fortify"
        }
      }
    }
  }
]);
