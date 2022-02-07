# TODO
## DSL
* Add support for "With(query).As(alias).Select(...)"
* Add support for "From(stringAlias)"

## Feature parity
* Qat's {def:...} (and others)

## Other inputs
* Ambiguous morse code streams?
* What about inputs like braille, morse?
* Words made from elements?


## Examples

`foo.*bar`:
```
    SELECT *
    FROM words
    WHERE text REGEXP "foo.*bar"
```

`foo{def:fruit}bar`:
```
    SELECT *
    FROM words
    WHERE
      words.word = "foo" || (
        SELECT
          dict.word
        FROM dict
        WHERE dict.definition LIKE "%fruit%"
      ) || "bar"
```

`foo.*bar&{elements}+`

Options:
* Treat "{elements}" as a source which repeats (i.e. there are an arbitrary # of streams)
