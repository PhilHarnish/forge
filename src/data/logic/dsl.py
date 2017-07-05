"""These objects are imported into every compiled logic problem"""
from data.logic import _dimension_factory, _model, _sugar

DimensionFactory = _dimension_factory._DimensionFactory
Model = _model._Model
abs = _sugar.sugar_abs
