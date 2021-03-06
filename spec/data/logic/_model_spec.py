import ast

from data.logic import _dimension_factory, _model, _reference, dsl
from spec.mamba import *

with description('_model._Model constructor'):
  with before.each:
    self.factory = _dimension_factory._DimensionFactory()

  with it('handles simple input'):
    expect(calling(_model._Model, self.factory)).not_to(raise_error)

with description('_model._Model usage'):
  with before.each:
    self.factory = _dimension_factory._DimensionFactory()
    self.model = _model._Model(self.factory)
    self.andy, self.bob, self.cynthia = self.factory(
        name=['andy', 'bob', 'cynthia'])
    self.cherries, self.dates, self.figs = self.factory(
        fruit=['cherries', 'dates', 'figs'])
    self._10, self._11, self._11 = self.factory(age=[10, 11, 11])

  with description('constraints'):
    with it('accumulates constraints one at a time'):
      expect(self.model.constraints).to(have_len(0))
      self.model(self.andy == self.cherries)
      expect(self.model.constraints).to(have_len(1))
      self.model(self.dates == self.bob)
      expect(self.model.constraints).to(have_len(2))
      self.model(self.cherries != self.bob)
      expect(self.model.constraints).to(have_len(3))

    with it('accumulates constraints all at once'):
      self.model(
          self.andy == self.cherries,
          self.dates == self.bob,
          self.cherries != self.bob,
      )
      expect(self.model.constraints).to(have_len(3))
      expect(str(self.model)).to(look_like("""
        assign:
          name["andy"].fruit["cherries"] in {0,1}
          name["bob"].fruit["dates"] in {0,1}
          name["bob"].fruit["cherries"] in {0,1}

        subject to:
          (name["andy"].fruit["cherries"] == True)
          (name["bob"].fruit["dates"] == True)
          (name["bob"].fruit["cherries"] == False)
      """))

    with it('accumulates AST expressions'):
      self.model(
          ast.parse('11 == "cherries"').body
      )
      expect(str(self.model)).to(look_like("""
        assign:
          fruit["cherries"].age[11] in {0,1}
        
        subject to:
          (fruit["cherries"].age[11] == True)
      """))

    with it('accumulates AST calls'):
      self.model(
          ast.parse('max(10, 11) == "cherries" == True').body
      )
      expect(str(self.model)).to(look_like("""
        assign:
          fruit["cherries"].age[11] in {0,1}
        
        subject to:
          (fruit["cherries"].age[11] == True)
      """))

    with it('accumulates sugared calls'):
      self.model(
          dsl.all([self.cherries == 11])
      )
      expect(str(self.model)).to(look_like("""
        assign:
          fruit["cherries"].age[11] in {0,1}

        subject to:
          AND(fruit["cherries"].age[11])
      """))

  with description('resolve'):
    with it('resolves simple addresses'):
      reference = self.model.resolve('name["andy"]')
      expect(reference._constraints).to(equal({'name': 'andy'}))

    with it('resolves complex addresses'):
      reference = self.model.resolve('name["andy"].fruit["cherries"]')
      expect(reference._constraints).to(equal({
        'name': 'andy',
        'fruit': 'cherries'
      }))

    with it('resolves values'):
      reference = self.model.resolve_value('cherries')
      expect(reference._constraints).to(equal({
        'fruit': 'cherries',
      }))

    with it('resolves primitives'):
      reference = self.model.resolve_value(11)
      expect(reference).to(be_a(_reference.ValueReference))
      expect(reference.value()).to(equal(11))

  with description('coerce_value'):
    with it('converts value references back to values'):
      reference = self.model.resolve_value(11)
      expect(self.model.coerce_value(reference)).to(equal(11))

    with it('converts references back to values'):
      reference = (self.model.resolve_value('andy') ==
          self.model.resolve_value('cherries'))
      expect(str(self.model.coerce_value(reference))).to(equal(
        'name["andy"].fruit["cherries"] in {0,1}'
      ))

  with description('get_variables'):
    with it('returns empty result for empty query'):
      expect(str(self.model.get_variables({}))).to(equal(''))

    with it('returns empty results for weakly constrained query'):
      expect(str(self.model.get_variables({'name': 'andy'}))).to(equal(''))

    with it('returns 1 result for well constrained query'):
      result = self.model.get_variables({
        'name': 'andy',
        'fruit': 'cherries',
      })
      expect(result).to(have_len(1))
      expect(str(result)).to(equal('name["andy"].fruit["cherries"] in {0,1}'))

    with it('returns multiple results for well constrained query'):
      result = self.model.get_variables({
        'name': 'andy',
        'fruit': 'cherries',
        'age': 10,
      })
      expect(result).to(have_len(3))
      expect(str(result)).to(look_like("""
        name["andy"].fruit["cherries"] in {0,1}
        name["andy"].age[10] in {0,1}
        fruit["cherries"].age[10] in {0,1}
      """))

    with it('returns from a cache'):
      result_1 = self.model.get_variables({
        'name': 'andy',
        'fruit': 'cherries',
      })
      result_2 = self.model.get_variables({
        'name': 'andy',
        'fruit': 'cherries',
      })
      expect(result_1).to(have_len(len(result_2)))
      for a, b in zip(result_1, result_2):
        expect(a).to(be(b))

    with it('reifies partially constrained dimensions'):
      result = self.model.get_variables({
        'name': 'bob',
        'age': None,
      })
      expect(str(result)).to(equal(
          '(10*name["bob"].age[10] in {0,1} + 11*name["bob"].age[11] in {0,1})'
      ))

  with description('duplicate nouns with unique positions'):
    with before.each:
      self.factory = _dimension_factory._DimensionFactory()
      self.model = _model._Model(self.factory)
      self.gray, self.gray, self.blue = self.factory(
          color=['gray', 'gray', 'blue'])
      self._1, self._2, self._3 = self.factory(position=[1, 2, 3])

    with it('still reifies the unique value'):
      result = self.model.get_variables({
        'color': 'blue',
        'position': None,
      })
      expect(str(result)).to(equal(
          '(color["blue"].position[1] in {0,1}'
          ' + 2*color["blue"].position[2] in {0,1}'
          ' + 3*color["blue"].position[3] in {0,1})'
      ))

    with it('reifies multiple variables for the duplicate value'):
      result = self.model.get_variables({
        'color': 'gray',
        'position': None,
      })
      expect(str(result)).to(look_like("""
        (color["gray"].position[1] * 1)
        (color["gray"].position[2] * 2)
        (color["gray"].position[3] * 3)
      """))

    with it('specifies boolean Numberjack variables'):
      self.model(self.model.dimension_constraints())
      model_lines = str(self.model).split('\n')
      assignments = '\n'.join(filter(lambda line: ' in ' in line, model_lines))
      expect(assignments).to(look_like("""
        color["gray"].position[1] in {0,1}
        color["gray"].position[2] in {0,1}
        color["gray"].position[3] in {0,1}
        color["blue"].position[1] in {0,1}
        color["blue"].position[2] in {0,1}
        color["blue"].position[3] in {0,1}
      """))

  with description('duplicate nouns with ambiguous values'):
    with before.each:
      self.factory = _dimension_factory._DimensionFactory()
      self.model = _model._Model(self.factory)
      self.factory(name=['andy', 'bob', 'cynthia'])
      self.factory(color=['gray', 'blue'])
      self.factory(food=['apple', 'banana'])

    with it('specifies some Numberjack variables with ranges'):
      self.model(self.model.dimension_constraints())
      model_lines = str(self.model).split('\n')
      assignments = '\n'.join(filter(lambda line: ' in ' in line, model_lines))
      expect(assignments).to(look_like("""
        name["andy"].color["gray"] in {0,1}
        name["andy"].color["blue"] in {0,1}
        name["bob"].color["gray"] in {0,1}
        name["bob"].color["blue"] in {0,1}
        name["cynthia"].color["gray"] in {0,1}
        name["cynthia"].color["blue"] in {0,1}
        name["andy"].food["apple"] in {0,1}
        name["andy"].food["banana"] in {0,1}
        name["bob"].food["apple"] in {0,1}
        name["bob"].food["banana"] in {0,1}
        name["cynthia"].food["apple"] in {0,1}
        name["cynthia"].food["banana"] in {0,1}
        color["gray"].food["apple"] in {0..2}
        color["gray"].food["banana"] in {0..2}
        color["blue"].food["apple"] in {0..2}
        color["blue"].food["banana"] in {0..2}
      """))

  with description('get_solutions'):
    with it('returns a 4x3 table'):
      self.model(self.andy.cherries[10] == True)
      self.model(self.bob.dates[11] == True)
      self.model(self.cynthia.figs[11] == True)
      expect(self.model.load('Mistral').solve()).to(be_true)
      column_headings, cells = self.model.get_solutions()
      expect(column_headings).to(have_len(3))
      expect(column_headings).to(equal([
        'name', 'fruit', 'age',
      ]))
      expect(cells).to(have_len(3))
      for row in cells:
        expect(row).to(have_len(3))
      expect(cells).to(equal([
        [['andy'], ['cherries'], [10]],
        [['bob'], ['dates'], [11]],
        [['cynthia'], ['figs'], [11]]
      ]))

  with description('get_solutions_grid'):
    with it('returns a 4x3 table'):
      self.model(self.andy.cherries[10] == True)
      self.model(self.bob.dates[11] == True)
      self.model(self.cynthia.figs[11] == True)
      expect(self.model.load('Mistral').solve()).to(be_true)
      expect(self.model.get_solutions_grid()).to(look_like("""
      *	cherries	dates	figs		10	11	
      andy	1	0	0		1	0	
      bob	0	1	0		0	1	
      cynthia	0	0	1		0	1	
     
      10	1	0	0	
      11	0	1	1	
      """))

  with description('dimension_constraints'):
    with it('enforces cardinality constraints (with duplicate scalar values)'):
      result = self.model.dimension_constraints(types=(
        _dimension_factory.Cardinality,
        _dimension_factory.UniqueCardinality,
        _dimension_factory.TotalCardinality,
      ))
      s = '\n'.join(sorted(
          str(result).replace(' | 0 in [1,1] 1 in [1,1] ', '').split('\n')
      ))
      expect(s).to(look_like("""
        ((fruit["cherries"].age[10] + fruit["dates"].age[10] + fruit["figs"].age[10]) == 1)
        ((fruit["cherries"].age[11] + fruit["dates"].age[11] + fruit["figs"].age[11]) == 2)
        ((name["andy"].age[10] + name["bob"].age[10] + name["cynthia"].age[10]) == 1)
        ((name["andy"].age[11] + name["bob"].age[11] + name["cynthia"].age[11]) == 2)
        ((name["andy"].fruit["cherries"] + name["andy"].fruit["dates"] + name["andy"].fruit["figs"]) == 1)
        ((name["andy"].fruit["cherries"] + name["bob"].fruit["cherries"] + name["cynthia"].fruit["cherries"]) == 1)
        ((name["andy"].fruit["dates"] + name["bob"].fruit["dates"] + name["cynthia"].fruit["dates"]) == 1)
        ((name["andy"].fruit["figs"] + name["bob"].fruit["figs"] + name["cynthia"].fruit["figs"]) == 1)
        ((name["bob"].fruit["cherries"] + name["bob"].fruit["dates"] + name["bob"].fruit["figs"]) == 1)
        ((name["cynthia"].fruit["cherries"] + name["cynthia"].fruit["dates"] + name["cynthia"].fruit["figs"]) == 1)
        (fruit["cherries"].age[10] != fruit["cherries"].age[11])
        (fruit["dates"].age[10] != fruit["dates"].age[11])
        (fruit["figs"].age[10] != fruit["figs"].age[11])
        (name["andy"].age[10] != name["andy"].age[11])
        (name["bob"].age[10] != name["bob"].age[11])
        (name["cynthia"].age[10] != name["cynthia"].age[11])
      """))

    with it('enforces cardinality constraints (with unique scalar values)'):
      self.factory = _dimension_factory._DimensionFactory()
      self.model = _model._Model(self.factory)
      self.factory(age=[10, 11, 12])
      self.factory(name=['andy', 'bob', 'cynthia'])
      self.factory(fruit=['cherries', 'dates', 'figs'])
      result = self.model.dimension_constraints(types=(
        _dimension_factory.Cardinality,
        _dimension_factory.UniqueCardinality,
        _dimension_factory.TotalCardinality,
      ))
      s = '\n'.join(sorted(
          str(result).replace(' | 0 in [1,1] 1 in [1,1] ', '').split('\n')
      ))
      expect(s).to(look_like("""
          ((name["andy"].fruit["cherries"] + name["andy"].fruit["dates"] + name["andy"].fruit["figs"]) == 1)
          ((name["andy"].fruit["cherries"] + name["bob"].fruit["cherries"] + name["cynthia"].fruit["cherries"]) == 1)
          ((name["andy"].fruit["dates"] + name["bob"].fruit["dates"] + name["cynthia"].fruit["dates"]) == 1)
          ((name["andy"].fruit["figs"] + name["bob"].fruit["figs"] + name["cynthia"].fruit["figs"]) == 1)
          ((name["bob"].fruit["cherries"] + name["bob"].fruit["dates"] + name["bob"].fruit["figs"]) == 1)
          ((name["cynthia"].fruit["cherries"] + name["cynthia"].fruit["dates"] + name["cynthia"].fruit["figs"]) == 1)
          AllDiff(age.fruit["cherries"], age.fruit["dates"], age.fruit["figs"])
          AllDiff(age.name["andy"], age.name["bob"], age.name["cynthia"])
      """))

    with it('enforces cardinality constraints (with ambiguous scalar values)'):
      self.factory = _dimension_factory._DimensionFactory()
      self.model = _model._Model(self.factory)
      self.factory(name=['andy', 'bob', 'cynthia'])
      self.factory(color=['gray', 'blue'])
      self.factory(food=['apple', 'banana'])
      result = self.model.dimension_constraints(types=(
        _dimension_factory.Cardinality,
        _dimension_factory.UniqueCardinality,
        _dimension_factory.TotalCardinality,
      ))
      s = '\n'.join(sorted(
          str(result).replace(' | 0 in [1,1] 1 in [1,1] ', '').split('\n')
      ))
      expect(s).to(look_like("""
        ((color["gray"].food["apple"] + color["gray"].food["banana"] + color["blue"].food["apple"] + color["blue"].food["banana"]) == 3)
        (name["andy"].color["gray"] != name["andy"].color["blue"])
        (name["andy"].food["apple"] != name["andy"].food["banana"])
        (name["bob"].color["gray"] != name["bob"].color["blue"])
        (name["bob"].food["apple"] != name["bob"].food["banana"])
        (name["cynthia"].color["gray"] != name["cynthia"].color["blue"])
        (name["cynthia"].food["apple"] != name["cynthia"].food["banana"])
      """))

    with it('enforces inference constraints'):
      result = self.model.dimension_constraints(
          types=(
            _dimension_factory.Inference,
            _dimension_factory.ValueSumsInference,
          ))
      expect(result).to(have_len(18))
      s = '\n'.join(sorted(
          re.sub(r'\.|name|fruit|age', '', str(result)).split('\n')
      ))
      expect(s).to(look_like("""
        ((["andy"]["cherries"] + ["andy"][10] + ["cherries"][10]) != 2)
        ((["andy"]["dates"] + ["andy"][10] + ["dates"][10]) != 2)
        ((["andy"]["figs"] + ["andy"][10] + ["figs"][10]) != 2)
        ((["bob"]["cherries"] + ["bob"][10] + ["cherries"][10]) != 2)
        ((["bob"]["dates"] + ["bob"][10] + ["dates"][10]) != 2)
        ((["bob"]["figs"] + ["bob"][10] + ["figs"][10]) != 2)
        ((["cynthia"]["cherries"] + ["cynthia"][10] + ["cherries"][10]) != 2)
        ((["cynthia"]["dates"] + ["cynthia"][10] + ["dates"][10]) != 2)
        ((["cynthia"]["figs"] + ["cynthia"][10] + ["figs"][10]) != 2)
        (["andy"]["cherries"] <= (["andy"][11] == ["cherries"][11]))
        (["andy"]["dates"] <= (["andy"][11] == ["dates"][11]))
        (["andy"]["figs"] <= (["andy"][11] == ["figs"][11]))
        (["bob"]["cherries"] <= (["bob"][11] == ["cherries"][11]))
        (["bob"]["dates"] <= (["bob"][11] == ["dates"][11]))
        (["bob"]["figs"] <= (["bob"][11] == ["figs"][11]))
        (["cynthia"]["cherries"] <= (["cynthia"][11] == ["cherries"][11]))
        (["cynthia"]["dates"] <= (["cynthia"][11] == ["dates"][11]))
        (["cynthia"]["figs"] <= (["cynthia"][11] == ["figs"][11]))
      """))

    with it('enforces inference constraints (for ambiguous values)'):
      self.factory = _dimension_factory._DimensionFactory()
      self.model = _model._Model(self.factory)
      self.factory(name=['andy', 'bob', 'cynthia'])
      self.factory(color=['gray', 'blue'])
      self.factory(food=['apple', 'banana'])
      result = self.model.dimension_constraints(
          types=(
            _dimension_factory.Inference,
            _dimension_factory.ValueSumsInference,
          ))
      s = '\n'.join(sorted(
          re.sub(r'\.|name|fruit|age', '', str(result)).split('\n')
      ))
      expect(s).to(look_like("""
        ((["andy"]color["blue"] + ["bob"]color["blue"] + ["cynthia"]color["blue"]) == (color["blue"]food["apple"] + color["blue"]food["banana"]))
        ((["andy"]color["gray"] + ["bob"]color["gray"] + ["cynthia"]color["gray"]) == (color["gray"]food["apple"] + color["gray"]food["banana"]))
        ((["andy"]food["apple"] + ["bob"]food["apple"] + ["cynthia"]food["apple"]) == (color["gray"]food["apple"] + color["blue"]food["apple"]))
        ((["andy"]food["banana"] + ["bob"]food["banana"] + ["cynthia"]food["banana"]) == (color["gray"]food["banana"] + color["blue"]food["banana"]))
      """))

    with description('disable constraints'):
      with it('normally returns constraints'):
        self.model.load('Mistral')
        expect(self.model.constraints).not_to(be_empty)

      with it('removes all constraints'):
        self.model.disable_constraints()
        self.model.disable_inference()
        self.model.load('Mistral')
        expect(self.model.constraints).to(be_empty)

      with it('removes specified constraints'):
        for c in _model._DEFAULT_CONSTRAINTS:
          self.model.disable_inference(c)
        expect(self.model.constraints).to(be_empty)

  with description('load'):
    with it('applies dimensional constraints before loading'):
      expect(str(self.model)).to(look_like("""
        assign:
                 
        subject to:
      """))
      expect(len(self.model.constraints)).to(be(0))
      self.model.load('Mistral')
      expect(len(self.model.constraints)).to(be_above(60))

    with it('remembers preferred solver'):
      self.model.solve_with('MiniSat')
      expect(self.model.get_solver()).to(equal(['MiniSat']))
