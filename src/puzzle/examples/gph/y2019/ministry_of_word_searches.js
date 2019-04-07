var SEEK = (
    'great work your first clue is the answer holds nine letters ok you must now isolate the unique valid wordsearch!'
).toUpperCase();
var YELLOWS = ['#ff0', '#ee0'];

function findGrid() {
    const cells = $$('td');
    let row = [];
    const grid = [];
    for (var i = 0; i < cells.length; i++) {
        row.push(cells[i]);
        if (row.length === 11) {
            grid.push(row);
            row = [];
        }
    }
    return grid;
}

function findWord(grid, word, incomplete = false) {
    for (let row = 0; row < grid.length; row++) {
        for (let col = 0; col < grid[row].length; col++) {
            scanWordDirections(grid, row, col, word, incomplete);
        }
    }
}
function scanWordDirections(grid, row, col, word, incomplete) {
    for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
            if (dr === 0 && dc === 0) {
                continue;
            }
            if (scanWord(grid, row, col, dr, dc, word, incomplete)) {
                scanWord(grid, row, col, dr, dc, word, incomplete, true);
            }
        }
    }
}
function scanWord(grid, row, col, dr, dc, word, incomplete, mark = false) {
    let i = 0;
    let off = 0;
    let ignored = 0;
    let matched = 0;
    if (mark) {
        grid[row][col].wordStart = true;
    }
    while (i < word.length) {
        if (row < 0 || row >= grid.length) {
            row = (row + grid.length) % grid.length;
            return false;
        }
        if (col < 0 || col >= grid[row].length) {
            col = (col + grid[row].length) % grid[row].length;
            return false;
        }
        if (!grid[row] || !grid[row][col]) {
            debugger;
        }
        const cell = grid[row][col];
        if (word[i] === cell.innerText) {
            if (mark && cell.hasWord) {
                cell.extract = true;
            }
            matched += 1;
        }
        if (word[i] !== cell.innerText) {
            if (mark) {
                cell.broken = true;
            }
            if (incomplete) {
                // Special rules.
                off += 1;
                if (cell.hasWord) {
                    ignored += 1;
                } else {
                    if (mark) {
                        cell.broken = true;
                    }
                }
            } else {
                return false;
            }
        } else if (mark) {
            if (word === 'OK') {
                cell.okWord = true;
            } else {
                cell.hasWord = true;
            }
            //if (cell.)
        }
        i += 1;
        row += dr;
        col += dc;
    }
    if (!matched) {
        return false;
    } else if (ignored >= 2) {
        return false;
    } else if (off) {
        return (off / word.length) <= .25;
    }
    return true;
}


function higlight() {
    let i = 0;
    let nthWord = 0;
    const cells = $$('td');
    for (let cell of cells) {
        cell.style.backgroundColor = 'transparent';
        if (cell.wordStart) {
            cell.style.fontWeight = '800';
        }
        if (cell.broken) {
            cell.style.backgroundColor = 'red';
        } else if (cell.extract) {
            cell.style.backgroundColor = 'green';
        } else if (cell.okWord) {
            cell.style.backgroundColor = 'green';
        } else if (cell.hasWord) {
            cell.style.backgroundColor = 'skyblue';
        } else if (cell.innerText === SEEK[i]) {
            i++;
            cell.style.backgroundColor = YELLOWS[nthWord % 2];
        }
        if (SEEK[i] === ' ') {
            i++;
            nthWord++;
        }
    }
    console.log('Found:', SEEK.slice(0, i));
}

var grid = findGrid();
findWord(grid, 'TRUDEAU');  // lots of them... 23.
findWord(grid, 'CAMPBELL', true);  // 19.
findWord(grid, 'TURNER', true);  // 17.
findWord(grid, 'DIEFENBAKER', true);  // 13.
findWord(grid, 'BENNETT', true);  // 11.
findWord(grid, 'LAURIER', true);  // 7.
findWord(grid, 'BOWELL', true);  // 5.
findWord(grid, 'ABBOTT', true);  // 3.
findWord(grid, 'MACKENZIE', true);  // 2.
//findWord(grid, 'OK');

//findWord(grid, 'REBRAUK');  // ???
//findWord(grid, 'NETTEWOBRL');
//findWord(grid, 'BBOTTLL');
//findWord(grid, 'KERDTEFUNB');
//findWord(grid, 'MPBELLTT');

higlight();

// TRUDEAU
