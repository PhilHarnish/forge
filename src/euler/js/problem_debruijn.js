var _ = require("../../../third_party/underscore/underscore.js")._;

/**
 * @see http://www.1stworks.com/ref/RuskeyCombGen.pdf
 */

var LENGTH = 7;
var BASE = 5;

exports.preamble = ["Finding shortest debruijn-esque sequence for", LENGTH,
  "subsequence given an alphabet of length and special required criteria."
];

// Implementation constants.
var MAX = Math.pow(BASE, LENGTH - 1);
// There must be ceil(log_2(LENGTH + 1)) bits to store LENGTH digits.
// For example, LENGTH = 4 needs to hold up to 4 consecutive 0s in the 0
// bucket (0..4 inclusive) and requires 3 bits.
var BUCKET_SIZE = Math.ceil(Math.log(LENGTH + 1) / Math.log(2));
var ZEROS = "0000000000000"; // Cheap way to provide padded 0s.
var BUTTON_L = 0; // Arbitrary.
var BUTTON_R = 1; // Arbitrary.
var BUTTON_A = 2; // Arbitrary.
var MUST_VISIT = getMustVisit();

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
    var i;
    // Initialize.
    for (i = 0; i < MAX; i++) {
      vertices[i] = getNeighbors(i);
      dualVertices[i] = [];
    }
    // Create a dual of the graph.
    for (i = 0; i < MAX; i++) {
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
    for (i = 0; i < MAX; i++) {
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

function getMustVisit() {
  var result = [];
  var count = 0;
  var max = Math.pow(BASE, LENGTH);
  for (var i = 0; i < max; i++) {
    var sums = getSums(i);
    var numLeft = sums[BUTTON_L] % 4; // 4 lefts or rights cancel out.
    var numRight = sums[BUTTON_R] % 4;
    var netOneTurn = Math.abs(numLeft - numRight) % 2 == 1;
    var str = (ZEROS + i.toString(BASE)).slice(-LENGTH);
    var numDoubles = 0;
    var first = str[0];
    var lastDouble = false;
    for (var c = 1; c < str.length; c++) {
      if (first == str[c] && !lastDouble) {
        numDoubles++;
      }
      lastDouble = first == str[c];
      first = str[c];
    }
    var everyDigit = true;
    for (var s = 0; s < sums.length && everyDigit; s++) {
      everyDigit = everyDigit && (sums[s] > 0);
    }
    // Start: 78125.
    // w/ first two match: 15625
    // w/ 3rd is not 1st or 2nd: 12500
    // w/ 3rd is not A: 62500
    // w/ net 1 turn: 39062
    // w/ numDoubles: 18960
    // w/ everyDigit: 16800
    // ALL: 228
    // w/o first two match: 584
    // w/o 3rd is not a: 288
    // w/o net one turn: 384
    // w/o numDoubles >= 2: 576
    // w/o every digit: 3008
    if (str[0] == str[1] && // First two buttons match.
        str[1] != str[2] && // Button 3 does not match buttons one or two.
        str[2] != BUTTON_A && // Button 3 is not A.
        netOneTurn && // Net effect of one turn.
        numDoubles >= 2 && // At least two doubles.
        everyDigit && // Assumes each digit was also required.
        'no-op') { // For ease of commenting out individual lines above.
      result.push(i);
      count++;
    }
  }
  console.log("Num must visit:", count);
  return result;
}

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
  var result = [];
  for (var i = 0; i < BASE; i++) {
    result[i] = 0;
  }
  var converted = (ZEROS + n.toString(BASE)).slice(-LENGTH);
  for (var idx = 0; idx < converted.length; idx++) {
    var digit = Number(converted[idx]);
    result[digit]++;
  }
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

