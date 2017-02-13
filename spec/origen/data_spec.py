import collections

from expects import *
from src.origen import data

_TestClass = collections.namedtuple('_TestClass', ['name', 'lines'])

with describe('load_lines'):
  with it('loads empty input without errors'):
    result = data.load_lines([], _TestClass)
    expect(result).to(be_empty)

  with it('loads single group without errors'):
    result = data.load_lines([
      '[example]',
      'First',
    ], _TestClass)
    expect(result).to(have_key('example'))
    expect(result['example'].name).to(equal('example'))
    expect(result['example'].lines).to(equal(['First']))

  with it('loads multiple groups'):
    result = data.load_lines([
      '[example]',
      'First',
      '[another]',
      'Second',
    ], _TestClass)
    expect(result).to(have_keys('example', 'another'))
    expect(result['another'].name).to(equal('another'))
    expect(result['another'].lines).to(equal(['Second']))
