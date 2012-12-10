var MongolabFixture = require("./MongolabFixture.js");
module.exports = MongolabFixture.exports("items", [
  {
    "_id": {
      "$oid": "50bae6f9e4b0afba6ecc5a15"
    },
    "name": "canned food",
    "owned": true,
    "properties": {
      "food": true
    },
    "weight": 3
  },
  {
    "_id": {
      "$oid": "50bae6dbe4b0afba6ecc5a14"
    },
    "name": "bat",
    "properties": {
      "weapon": true
    },
    "owned": true,
    "weight": 2
  }
]);
