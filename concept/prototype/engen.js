var SEED = 1;

function tileStatus(position, tile) {
  var tx = tile[0];
  var ty = tile[1];
  var topLeft = roomMetadata(position);
  var right = roomMetadata(sumPoints(position, [1, 0]));
  var bottom = roomMetadata(sumPoints(position, [0, 1]));
  var door = Math.floor(ROOM_TILES / 2);
  var edge = ROOM_TILES - 1;
  var verticalEdge = tx % edge == 0;
  var horizontalEdge = ty % edge == 0;

  if (!horizontalEdge && !verticalEdge) {
    // The inside is always empty.
    return "room-vacant";
  } else if (horizontalEdge && verticalEdge) {
    // The corners are always filled.
    return "room-blocked";
  } else if (ty == 0 && !topLeft.top) {
    // Draw a small or wide door.
    return tx == door || topLeft.topWide ? "room-vacant" : "room-blocked";
  } else if (tx == 0 && !topLeft.left) {
    // Draw a small or wide door.
    return ty == door || topLeft.leftWide ? "room-vacant" : "room-blocked";
  } else if (tx == edge && !right.left) {
    // Draw a small or wide door.
    return ty == door || right.leftWide ? "room-vacant" : "room-blocked";
  } else if (ty == edge && !bottom.top) {
    // Draw a small or wide door.
    return tx == door || bottom.topWide ? "room-vacant" : "room-blocked";
  }
  return "room-blocked";
}

var METADATA_CACHE = {};
function roomMetadata(position) {
  var id = position.join("x");
  if (!(id in METADATA_CACHE)) {
    var rand = getRandGenerator(position);
    METADATA_CACHE[id] = {
      top: rand.bit(),
      topWide: rand.bit(),
      left: rand.bit(),
      leftWide: rand.bit()
    };
  }
  return METADATA_CACHE[id];
}

var RAND_CACHE = {};
var CACHE_BLOCK = 8;
function getRand(position) {
  var ox = position[0] % CACHE_BLOCK;
  var oy = position[1] % CACHE_BLOCK;
  // Position may be negative; correct that before proceeding.
  ox = ox < 0 ? ox + CACHE_BLOCK : ox;
  oy = oy < 0 ? oy + CACHE_BLOCK : oy;
  // Effectively rounds (bx, by) to nearest lower multiple of CACHE_BLOCK.
  var bx = position[0] - ox;
  var by = position[1] - oy;
  var id = bx + "x" + by;
  if (!(id in RAND_CACHE)) {
    RAND_CACHE[id] = [];
    var prng = Alea(bx, "x", by).uint32;
    var cache = RAND_CACHE[id];
    for (var y = 0; y < CACHE_BLOCK; y++) {
      cache[y] = [];
      var row = cache[y];
      for (var x = 0; x < CACHE_BLOCK; x++) {
        row[x] = prng();
      }
    }
  }
  return RAND_CACHE[id][oy][ox];
}

function getRandGenerator(position) {
  var rand = getRand(position);
  return {
    bit: function () {
      var result = rand & 1;
      rand >>= 1;
      return result;
    },
    bits: function (n) {
      var result = rand & ((1 << n) - 1);
      rand >>= n;
      return result;
    }
  };
}
