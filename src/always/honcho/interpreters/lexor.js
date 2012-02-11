// Lexer library.

var State = function (name, token) {
  this._name = name;
  this._token = token !== false;
  this._transitions = [];
};

State.prototype.on = function () {
  var next = Array.prototype.slice.call(arguments);
  this._transitions.push([next.shift(), next]);
};

State.prototype.lex = function (input, index) {
  index = index || 0;
  var remainder = input.slice(index);
  var result = {
    consumedInput: 0,
    state: this,
    tokens: []
  };

  var length = this._transitions.length;
  for (var i = 0; i < length; i++) {
    var transition = this._transitions[i];
    var regexp = transition[0];
    var transitions = transition[1].slice();
    var match = regexp.exec(remainder);
    if (match) {
      var lastTokenIndex = 0;
      while (transitions.length) {
        var state = transitions.shift();
        if (typeof state == "function") {
          transitions.unshift.apply(transitions,
              state(remainder, result.consumedInput, match[0].length));
        } else if (!isNaN(state)) {
          lastTokenIndex = state;
        } else if (state instanceof State) {
          if (state != result.state && state._token) {
            lastTokenIndex = lastTokenIndex || match[0].length;
            result.tokens.push(state._name +
                "(" + remainder.slice(result.consumedInput, lastTokenIndex) + ")");
          }
          result.consumedInput = lastTokenIndex;
          result.state = state;
        } else {
          throw new Error("Unknown transition", state);
        }
      }
      //result.consumedInput = Math.max(match[0].length, lastTokenIndex);
      break;
    }
  }

  return result;
};

exports.State = State;

var Lexer = function (state) {
  this._state = state;
  this._input = "";
  this._consumedInput = 0;
  this._lexedInput = 0;
  this._tokens = [];
  this._tokensQued = 0;
};

Lexer.prototype.update = function (input) {
  this._input += input;
};

Lexer.prototype.getNextToken = function () {
  var inputLength = this._input.length;
  var abort = 10;
  while (!this._tokensQued && this._lexedInput < inputLength && abort--) {
    var oldState = this._state;
    var lexed = this._state.lex(this._input, this._consumedInput);
    this._state = lexed.state;
    this._consumedInput += lexed.consumedInput;
    this._lexedInput = oldState == this._state ?
        lexed.consumedInput || inputLength :
        lexed.consumedInput;
    if (lexed.tokens) {
      this._tokensQued += lexed.tokens.length;
      this._tokens.push.apply(this._tokens, lexed.tokens);
    }
  }
  return this._tokensQued > 0 ?
      this._tokens[this._tokens.length - this._tokensQued--] : null;
};

exports.Lexer = Lexer;
