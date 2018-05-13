# DSL
The following statements will import convenience functions:

      import forge
      from puzzle import *

# `puzzle()`
* `source: str` Raw text for puzzle.
* `hint: str` Type hint for puzzle. Influences puzzle choice when more than one
  puzzle type matches input.
* `threshold: float` Minimum score needed for results. May reduce execution
  time.
