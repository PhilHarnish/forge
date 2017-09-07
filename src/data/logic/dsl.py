"""These objects are imported into every compiled logic problem"""
import Numberjack

from data.logic import _dimension_factory, _model, _sugar

DimensionFactory = _dimension_factory._DimensionFactory
Model = _model._Model
abs = _sugar.wrapped_call(Numberjack.Abs)
all = _sugar.wrapped_call(Numberjack.Conjunction)
all_diff = _sugar.wrapped_call(Numberjack.AllDiff)
any = _sugar.wrapped_call(Numberjack.Disjunction)
gcc = _sugar.wrapped_call(_sugar.gcc)
sum = _sugar.wrapped_call(Numberjack.Sum)
max = _sugar.wrapped_call(Numberjack.Max)
min = _sugar.wrapped_call(Numberjack.Min)
print = _sugar.deferred_call(print)

init = _sugar.init

variable = _sugar.Variable
