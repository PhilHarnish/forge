This directory organizes code related to solving logic puzzles.

# Execution for a sample program
This outlines how the following puzzle would be solved:

    The CEO is not the youngest.
    Andy is a year younger than Bob.
    Cathy is older than the Project Manager.
    Bob is either the CEO or the Project Manager.

## DSL program
First the puzzle would be transcribed into the DSL:

    name <= {Andy, Bob, Cathy}
    occupation <= {CEO, ProjectManager, Analyst}
    age <= {10, 11, 12}
    # The CEO is not the youngest.
    CEO.age > ProjectManager.age
    CEO.age > Analyst.age
    # Andy is a year younger than Bob.
    Andy.age + 1 == Bob.age
    # Cathy is older than the Project Manager.
    Cathy.age > ProjectManager.age
    # Bob is either the CEO or the Project Manager.
    Bob == CEO or Bob == ProjectManager

The comments in this source are converted to strings (so that they are
preserved) and then the rest is parsed with `ast.parse()`.

### Features: Comments
Comments are preserved in transpilation as str literals. Lazy hack.

## Transpiled program
The parsed result is converted using GrammarTransformer into a new AST which
looks like this:

    from data.logic.dsl import *
    dimensions = DimensionFactory()
    model = Model(dimensions)
    andy, bob, cathy = name = dimensions(name=['Andy', 'Bob', 'Cathy'])
    ceo, projectmanager, analyst = occupation = dimensions(occupation=['CEO',
       'ProjectManager', 'Analyst'])
    _10, _11, _12 = age = dimensions(age=[10, 11, 12])
    """# The CEO is not the youngest."""
    model(ceo.age > projectmanager.age)
    model(ceo.age > analyst.age)
    """# Andy is a year younger than Bob."""
    model(andy.age + 1 == bob.age)
    """# Cathy is older than the Project Manager."""
    model(cathy.age > projectmanager.age)
    """# Bob is either the CEO or the Project Manager."""
    model((bob == ceo) ^ (bob == projectmanager))

The resulting AST is executed with Python's `compile()` and `exec()` functions.
`model` is extracted from the locals created during `exec()`.

### Features: "Sugar"
Several symbols are imported (including helpers from dsl module)

### Features: Dimensions
`name <= {Andy, Bob, Cathy}` instantiates a new dimension and several local
variables.

### Features: Implicit modelling
Expressions are automatically wrapped in calls to "model()".

### Features: Control flow
Simple `if/else` expressions are converted to boolean logic. Supported examples
include:

    # Boolean implications.
    if A:
      B == True
    else:
      C == True
    # Conditional assignments.
    if A:
      b = 10
    else:
      c = 20

As well as combinations of those two features.

## Runtime model
`exec()` will execute the converted AST like an ordinary Python program and this
will cause yet-another representation to be created at runtime. Each of the
dimension variables from the transpiled program use operator overloading to
keep track of operations performed, in the order Python would normally perform
them.

For example, `model(ceo.age > projectmanager.age)` starts by loading `ceo` and
its `age` attribute, then the same for `projectmanager`, then performs
`ceo.age.__gt__(projectmanager.age)` and finally passes the result to a call to
`model()`.

Attribute resolution on dimensions results in accumulated dimension constraints.
That is, initially `ceo` could refer to "CEO" with any name or age. When `age`
is referenced the constraint is `{occupation: CEO, age: None}` which implies the
the reference is intended to represent _all_ possible ages. How this is
accomplished is explained in more detail in the Numberjack model section.

Regardless, this phase of execution is entirely symbolic. The result is a new
model of the system which is (not coincidentally) stored using AST nodes. For
example, `ceo.age > projectmanager.age` is an `ast.LtE` object where the left
and right values are `ast.Name` objects with `id` of the form
`occupation["xyz"].age[None]`.

### Features: "Sugar"
Some python builtins have been replaced with intuitive substitutes. (See
`dsl.py` for implementation.)

* `abs`: Wrapper of Numberjack.Abs.
* `all`: Wrapper of Numberjack.Conjunction.
* `any`: Wrapper of Numberjack.Disjunction.
* `sum`: Wrapper of Numberjack.Sum.
* `print`: Defers a call to print until after a solution is found. If the
  program is evaluated multiple times then the `print()` statements are
  executed once per solution.

## Compiled model
The result of each expression is passed as an argument to `model()` (see
"Transpiled program" above). ExprTransformer performs its own AST traversal
with a goal of reducing each expression to Numberjack predicates.

### Features: Predicates
References are combined into Predicate objects which contain 1 or more
Numberjack predicates. For example, `Andy == Analyst` translates to a single
reference `name["Andy"].occupation["Analyst"]` while `Andy == Analyst == 10`
would have 2 additional references `name["Andy"].age[10]` and
`occupation["Analyst"].age[10]` all internal to the same Predicate object. This
makes the following expressions possible:

    model(andy == analyst == 10)
    model(andy == analyst == 10 == True)
    model(andy == analyst == 10 == False)
    
### Features: Debugging
Strict type checking (see `_fail()`) and `print()` pass through this layer. The
print()

## Numberjack model
The ExprTransformer compiles `Numberjack.Model.model()` arguments. Here is the
Numberjack model produced from the example above:

    assign:
      occupation["CEO"].age[10] in {0,1}
      occupation["CEO"].age[11] in {0,1}
      occupation["CEO"].age[12] in {0,1}
      occupation["ProjectManager"].age[10] in {0,1}
      occupation["ProjectManager"].age[11] in {0,1}
      occupation["ProjectManager"].age[12] in {0,1}
      occupation["Analyst"].age[10] in {0,1}
      occupation["Analyst"].age[11] in {0,1}
      occupation["Analyst"].age[12] in {0,1}
      name["Andy"].age[10] in {0,1}
      name["Andy"].age[11] in {0,1}
      name["Andy"].age[12] in {0,1}
      name["Bob"].age[10] in {0,1}
      name["Bob"].age[11] in {0,1}
      name["Bob"].age[12] in {0,1}
      name["Cathy"].age[10] in {0,1}
      name["Cathy"].age[11] in {0,1}
      name["Cathy"].age[12] in {0,1}
      name["Bob"].occupation["CEO"] in {0,1}
      name["Bob"].occupation["ProjectManager"] in {0,1}
    
    subject to:
      ((10*occupation["CEO"].age[10] + 11*occupation["CEO"].age[11] + 12*occupation["CEO"].age[12]) > (10*occupation["ProjectManager"].age[10] + 11*occupation["ProjectManager"].age[11] + 12*occupation["ProjectManager"].age[12]))
      ((10*occupation["CEO"].age[10] + 11*occupation["CEO"].age[11] + 12*occupation["CEO"].age[12]) > (10*occupation["Analyst"].age[10] + 11*occupation["Analyst"].age[11] + 12*occupation["Analyst"].age[12]))
      (((10*name["Andy"].age[10] + 11*name["Andy"].age[11] + 12*name["Andy"].age[12]) + 1) == (10*name["Bob"].age[10] + 11*name["Bob"].age[11] + 12*name["Bob"].age[12]))
      ((10*name["Cathy"].age[10] + 11*name["Cathy"].age[11] + 12*name["Cathy"].age[12]) > (10*occupation["ProjectManager"].age[10] + 11*occupation["ProjectManager"].age[11] + 12*occupation["ProjectManager"].age[12]))
      ((name["Bob"].occupation["CEO"] + name["Bob"].occupation["ProjectManager"]) == 1)

### Features: Reified dimension scalars
When the options for a dimension are numbers it is possible to do arithmetic
or inequality comparisons with the following (implicit) matrix multiplication:

    10*occupation["CEO"].age[10] + 11*occupation["CEO"].age[11] + 12*occupation["CEO"].age[12]

## Numberjack solution
Finally, a solution is extracted from the model by iterating each pair of
constraints. The first defined dimension determines the column and other values
are determined by that value.

       name |     occupation | age
       Andy |        Analyst |  10
        Bob | ProjectManager |  11
      Cathy |            CEO |  12

### Features: Multiple solutions
Repeated calls for solutions will produce more results, if any.

### Features: Multiple True values
In some cases a row may have multiple values (e.g. multiple occupations) or a
column could have multiple matches (e.g. multiple people with same age). In
both cases the output should produce correct results. Something like this:

       name |     occupation | age
       Andy |   Analyst, CEO |  11
        Bob | ProjectManager |  11
      Cathy |            CTO |  12


# TODO

* Support `if cond: {A, B, C} == {X, Y, Z}`.
* Support `for x in y: 1 <= foo <= 4`
* Optimize `a.reified == b.reified` to `all(a[x] == b[x] for x in reified)`.
