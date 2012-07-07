function tileStatus(position, rx, ry) {
  var door = Math.floor(ROOM_TILES / 2);
  if (rx == door || ry == door) {
    return "room-vacant";
  } else if (rx % (ROOM_TILES - 1) && ry % (ROOM_TILES - 1)) {
    return "room-vacant";
  }
  return "room-blocked";
}

