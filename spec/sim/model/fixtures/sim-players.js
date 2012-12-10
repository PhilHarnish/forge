var MongolabFixture = require("./MongolabFixture.js");
module.exports = MongolabFixture.exports("players", [
  {
    "_id": {
      "$oid": "50b6f69be4b0dbae32c8ece1"
    },
    "name": "philharnish",
    "stats": {
      "health": 50,
      "hunger": 50,
      "energy": 80
    },
    "ui": {
      "mode": {
        "explore": "flight",
        "rest": "study"
      }
    }
  }
]);
