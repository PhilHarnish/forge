const fs = require('fs');
const process = require('process');

const EIGHT_CAPS = /[acefghijlmopstuw]/;
const EIGHT_LOWER = /[abcdfghijlmnopqrtuwy]/;
const EIGHT_ALL = new RegExp(
    `^(${EIGHT_CAPS.source}+|${EIGHT_CAPS.source}?${EIGHT_LOWER.source}+)$`);

const EIGHT_SEGMENT_MODE = true;

const results = [];
for (let i = 0; i < 20; i++) {
  results.push([]);
}


const topWords = /** @type {Array<string>} */ (
    fs.readFileSync(process.argv[2], 'utf8').split('\n'));
const topMap = /** @type {Object<string, number>} */{
  'ox': -1,
  'aka': -1,
  'cog': -1,
  'eon': -1,
  'flu': -1,
  'gap': -1,
  'gel': -1,
  'ion': -1,
  'orc': -1,
  'tab': -1,
  'item': -1,
  'biped': -1,
  'spore': -1,
  'toxic': -1,
  'cleric': -1,
  'cocoon': -1,
  'subway': -1,
  'zealot': -1,
  'cathode': -1,
  'coexist': -1,
  'figment': -1,
  'paladin': -1,
  'theorem': -1,
  'syringe': -1,
  'biologist': -1,
  'cataclysm': -1,
  'cuneiform': -1,
  'fabricate': -1,
  'terrorism': -1,
};

// @ 4 letters, ixxx.

const filter = new RegExp('^[a-z]{0,16}$');
for (let i = 0; i < topWords.length; i++) {
  let word = topWords[i];
  if (word.match(filter) && !(word in topMap)) {
    topMap[word] = i;
  }
}

fs.readFile(process.argv[3], 'utf8', (err, data) => {
  const lines = data.split('\n');
  for (let line of lines) {
    if (line[0] >= 'A' && line[0] <= 'Z') {
      // Skip lines with capital letters.
      continue;
    } else if (line.length > 16) {
      continue;
    } else if (!(line in topMap)) {
      continue;
    } else if (topMap[line] > 60000) {
      //console.log('skipping', line, topMap[line]);
      continue;
    }
    if (EIGHT_SEGMENT_MODE && !EIGHT_ALL.test(line)) {
      continue;
    }
    results[line.length].push(line);
  }
  for (let result of results) {
    for (let word of result) {
      console.log(word);
    }
  }
});

/*
abot
costello
Z Skip
do not skip
A Skip
 */
