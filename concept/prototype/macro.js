var state;

$(function() {
  $("#start-button").click(start);
  start();
});

function start() {
  console.log("Starting.");
  var prng = getRandGenerator(SEED);
  state = {
    prng: prng,
    floors: {}
  };
  var id = generateFloor(state);
  visit(state, id);
  var dropzone = $("#dropzone");
  dropzone.html(drawFloors(state));
}

function visit(state, location) {
  state.location = location;
  var floor = state.floors[location];
  floor.status.safe = true;
  floor.status.visited = true;
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

function getFloor(state, id) {
  var floor = state.floors[id];
  if (!floor) {
    floor = {
      id: id,
      status: {
        safe: false,
        visited: false
      },
      neighbors: []
    };
    state.floors[id] = floor;
  }
  return floor;
}

function drawFloors(state) {
  var floors = [];
  var visit = function (id) {
    var floor = getFloor(state, id);
    floors.push(drawFloor(floor));
    for (var i = 0; i < floor.neighbors.length; i++) {
      visit(floor.neighbors[i]);
    }
    return floors;
  };
  return visit(state.location).join("");
}

function drawFloor(floor) {
  var classes = [];
  for (var key in floor.status) {
    if (floor.status[key]) {
      classes.push(key);
    }
  }
  return "<li id='" + floor.id + "' class='" + classes.join(" ") + "'></li>";
}

function getIcon(icon) {
  return "<span class='icon'>" +
      "<span class='inner-icon'>" + icon + "</span>" +
      "<span class='percentage'>" + icon + "</span>" +
      "</span>";
}
