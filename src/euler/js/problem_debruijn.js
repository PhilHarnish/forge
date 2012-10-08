var _ = require("../../../third_party/underscore/underscore.js")._;

/**
 * @see http://www.1stworks.com/ref/RuskeyCombGen.pdf
 */

var LENGTH = 7;
var BASE = 5;
var FORBIDDEN = [];
var REQUIRED = [];
var OTHER = [];

exports.preamble = ["Finding shortest debruijn-esque sequence for", LENGTH,
  "subsequence given an alphabet of length", BASE, "avoiding [" +
  FORBIDDEN.join("], [") + "] requiring [" + REQUIRED.join("], [") + "] and",
  OTHER.length, "other matching functions."
];

// Implementation constants.

// There must be ceil(log_2(LENGTH + 1)) bits to store LENGTH digits.
// For example, LENGTH = 4 needs to hold up to 4 consecutive 0s in the 0
// bucket (0..4 inclusive) and requires 3 bits.
var BUCKET_SIZE = Math.ceil(Math.log(LENGTH + 1) / Math.log(2));
var BUCKET_BITMASK = (1 << BUCKET_SIZE) - 1;
var ZEROS = "0000000000000"; // Cheap way to provide padded 0s.

exports.solutions = {
  /**
   * properties indexes the sum of digits for each BASE digit.
   * 00000, 00001, 00010, 00011, 00100, 00101, 00110, 00111
   */
  brute_force: function () {
    if (BUCKET_SIZE * BASE > 31) {
      throw new Error("Alphabet/length too large for JS Number type.");
    }
    var vertices = [];
    var dualVertices = [];
    var sums = [];
    var max = Math.pow(BASE, LENGTH - 1);
    var i;
    // Initialize.
    for (i = 0; i < max; i++) {
      vertices[i] = getNeighbors(i);
      dualVertices[i] = [];
      sums[i] = getSums(i);
    }
    // Create a dual of the graph.
    for (i = 0; i < max; i++) {
      var current = vertices[i];
      for (var outgoing = 0; outgoing < BASE; outgoing++) {
        dualVertices[current[outgoing]].push(i);
      }
    }
    // Find spanning tree of dual graph.
    var spanningEdges = getSpanningTreeNoRecurse(dualVertices);

    // Output cycle.
    var result = traverse(vertices, spanningEdges);

    // Assert everything is present.
    var tested = [];
    var elements = result.slice(0, LENGTH - 1); // Leave 1 char off.
    var looped = result.concat();
    // Add the first LENGTH elements from result to make a full cycle.
    for (i = 0; i < LENGTH; i++) {
      looped.push(looped[i]);
    }
    elements.unshift(0); // To prepare for first shift() call.
    for (i = LENGTH; i < looped.length; i++) {
      elements.shift();
      elements.push(looped[i]);
      tested[parseInt(elements.join(""), BASE)] = true;
    }
    for (i = 0; i < max; i++) {
      if (!tested[i]) {
        throw new Error(i + " was never visited.");
      }
    }

    return result.length;
  },

  full_cycle: function () {
    var a = []; // ???
    var result = [];
    function db (t, p) { // ???
      if (t > LENGTH) { // ???
        if (LENGTH % p == 0) { // ???
          for (var j = 1; j <= p; j++) {
            result.push(a[j] || 0);
          }
        }
      } else {
        a[t] = a[t - p] || 0;
        db(t + 1, p);
        for (var i = (a[t - p] || 0) + 1; i < BASE; i++) {
          a[t] = i;
          db(t + 1, t);
        }
      }
    }
    db(1, 1);
    return result.length;
  }
};

function getNeighbors(n) {
  var result = [];
  // Convert to base BASE and take the last LENGTH - 1 digits.
  var converted = n.toString(BASE);
  var prefix = (ZEROS + converted).slice(1 - LENGTH);
  for (var i = 0; i < BASE; i++) {
    var suffix = (prefix + i).slice(1);
    result.push(parseInt(suffix, BASE));
  }
  return result;
}

function getSums(n) {
  if (BASE > 10) {
    throw new Error("Only supports decimal digits.");
  }
  var result = 0;
  var converted = n.toString(BASE);
  for (var idx = 0; idx < converted.length; idx++) {
    var digit = Number(converted[idx]);
    result += 1 << (digit * BUCKET_SIZE);
  }
  // Since the converted string isn't 0 padded on the left, add missing 0s.
  result += LENGTH - converted.length;
  return result;
}

function getSpanningTreeNoRecurse(graph) {
  // Start by visiting 0.
  var path = [0];
  var visited = [true];
  var spanningEdges = {};
  while (path.length) {
    var current = _.last(path);
    var vertex = graph[current];
    var outgoing;
    for (outgoing = 0; outgoing < vertex.length; outgoing++) {
      var next = vertex[outgoing];
      if (!visited[next]) {
        visited[next] = true;
        // Store edge by concatenating and converting base.
        var from = (ZEROS + current.toString(BASE)).slice(1 - LENGTH);
        var to = (ZEROS + next.toString(BASE)).slice(1 - LENGTH);
        // NB: Reverse edges.
        var edge = parseInt(to + from, BASE);
        spanningEdges[edge] = true;
        path.push(next);
        break;
      }
    }
    if (outgoing == vertex.length) {
      // Exhausted every outgoing path from the last vertex in path.
      path.pop();
    }
  }
  return spanningEdges;
}

function traverse(graph, spanningEdges) {
  // Location of last character.
  // Eg, for LENGTH == 3, last character is 2nd, or 1.
  var outgoing = LENGTH - 2;
  var result = [];
  var current = 0;
  var currentStr = "00";
  var vertex = graph[current];
  while (vertex.length) {
    // Find next edge.
    var size = vertex.length;
    var next  = vertex.pop();
    while (size--) {
      var nextStr = (ZEROS + next.toString(BASE)).slice(1 - LENGTH);
      var edge = parseInt(currentStr + nextStr, BASE);
      if (spanningEdges[edge]) {
        vertex.unshift(next);
        next = vertex.pop();
      } else {
        break;
      }
    }
    result.push(nextStr[outgoing]); // Take the last characacter.
    vertex = graph[next];
    currentStr = nextStr;
  }
  return result;
}
