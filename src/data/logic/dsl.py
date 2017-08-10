"""These objects are imported into every compiled logic problem"""
import Numberjack

from data.logic import _dimension_factory, _model, _sugar

DimensionFactory = _dimension_factory._DimensionFactory
Model = _model._Model
abs = _sugar.wrapped_call(Numberjack.Abs)
all = _sugar.wrapped_call(Numberjack.Conjunction)
any = _sugar.wrapped_call(Numberjack.Disjunction)
sum = _sugar.wrapped_call(Numberjack.Sum)
print = _sugar.deferred_call(print)

init = _sugar.init
