var state;
var selectedPlayer;

$(function() {
  $("#start-button").click(start);
  start();
});

function start() {
  console.log("Starting.");
  var prng = getRandGenerator(SEED);
  state = {
    floors: {},
    players: {},
    prng: prng
  };
  var floorId = generateFloor(state);
  selectedPlayer = generatePlayer(state);
  visit(state, selectedPlayer, floorId);
  var dropzone = $("#dropzone");
  dropzone.html(drawFloors(state));
  dropzone.click(onClick);
}

function onClick(e) {
  visit(state, selectedPlayer, e.target.id);
}

function visit(state, playerId, floorId) {
  console.log("player", playerId, "visits", floorId);
  var player = state.players[playerId];
  if (player.floor) {
    // Remove from last floor.
    var lastFloor = getFloor(state, player.floor);
    lastFloor.players[playerId] = false;
  }
  var floor = state.floors[floorId];
  floor.status.safe = true;
  floor.status.visited = true;
  floor.players[playerId] = true;
  player.floor = floorId;
}

function getRandGenerator(seed) {
  var gen = Alea(seed).uint32;
  return {
    bit: function () {
      return gen() & 1;
    },
    bits: function (n) {
      return gen() & ((1 << n) - 1);
    },
    uint32: gen
  };
}

function generateFloor(state, parent) {
  var id = "floor" + state.prng.uint32();
  var floor = getFloor(state, id);
  if (parent) {
    floor.neighbors.push(parent);
  }
  floor.neighbors.push("floor" + state.prng.uint32());

  return id;
}

function generatePlayer(state) {
  var id = "player" + state.prng.uint32();
  state.players[id] = {
    floor: undefined
  };

  return id;
}

function getFloor(state, id) {
  var floor = state.floors[id];
  if (!floor) {
    floor = {
      id: id,
      neighbors: [],
      players: {},
      status: {
        safe: false,
        visited: false
      }
    };
    state.floors[id] = floor;
  }
  return floor;
}

function drawFloors(state) {
  var floors = [];
  var visit = function (id, occupied) {
    var floor = getFloor(state, id);
    floors.push(drawFloor(floor,
        occupied ? ["occupied"] : []));
    for (var i = 0; i < floor.neighbors.length; i++) {
      visit(floor.neighbors[i]);
    }
  };
  for (var i in state.players) {
    visit(state.players[i].floor, true);
  }
  return floors.join(" ");
}

function drawFloor(floor, classes) {
  for (var key in floor.status) {
    if (floor.status[key]) {
      classes.push(key);
    }
  }
  return "<li id='" + floor.id + "' class='" + classes.join(" ") + "'></li>";
}

function getIcon(icon) {
  return ["<span class='icon'>",
      "<span class='inner-icon'>", icon, "</span>",
      "<span class='percentage'>", icon, "</span>",
      "</span>"].join("");
}
