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
  selectedPlayer = getPlayer(state);
  visit(state, selectedPlayer, floorId);
  var dropzone = $("#dropzone");
  dropzone.append.apply(dropzone, drawFloors(state));
  dropzone.click(onClick);
}

function onClick(e) {
  visit(state, selectedPlayer, e.target.id);
}

function visit(state, player, floorId) {
  console.log("player", player[0].id, "visits", floorId);
  var floor = getFloor(state, floorId);
  floor.addClass("safe visited");
  floor.append(player);
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
    floor.append(generateDoor(parent));
  }
  floor.append(generateDoor("floor" + state.prng.uint32()));

  return id;
}

function generateDoor(destination) {
  return $(["<a href='#", destination, "'>door</a>"].join(""));
}

function getPlayer(state) {
  var id = "player" + state.prng.uint32();
  state.players[id] = $(["<p id='", id, "'></p>"].join(""));
  return state.players[id];
}

function getFloor(state, id) {
  var floor = state.floors[id];
  if (!floor) {
    state.floors[id] = $(["<li id='", id, "'></li>"].join(""));
  }
  return state.floors[id];
}

function drawFloors(state) {
  var floors = [];
  var visit = function (index, element) {
    var floor = getFloor(state, element.id);
    floors.push(floor);
    floor.children("a").each(visit);
  };
  for (var i in state.players) {
    // Pretend to visit an <a> element with floor ID.
    visit(null, {
      id: state.players[i].parent()[0].id
    });
  }
  return floors;
}

function getIcon(icon) {
  return ["<span class='icon'>",
      "<span class='inner-icon'>", icon, "</span>",
      "<span class='percentage'>", icon, "</span>",
      "</span>"].join("");
}
