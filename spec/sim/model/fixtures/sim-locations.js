var MongolabFixture = require("./MongolabFixture.js");
module.exports = MongolabFixture.exports("locations", [
  {
    "_id":{
      "$oid":"50b82462e4b0afba6ecc54b7"
    },
    "name":"locked door",
    "memorable":true,
    "x":0,
    "y":10,
    "z":0
  },
  {
    "_id":{
      "$oid":"50b82488e4b0afba6ecc54b8"
    },
    "name":"hostile",
    "memorable":false,
    "x":10,
    "y":10,
    "z":0
  },
  {
    "_id":{
      "$oid":"50b823fce4b0afba6ecc54b5"
    },
    "name":"base",
    "memorable":true,
    "x":0,
    "y":0,
    "z":0,
    "memorize":true
  }
]);
