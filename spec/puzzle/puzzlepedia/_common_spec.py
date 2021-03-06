from puzzle.puzzlepedia import _common
from spec.mamba import *

with description('_common_spec.format_label'):
  with it('is a no op for human readable inputs'):
    expect(_common.format_label('this is fine')).to(equal('this is fine'))

  with it('converts CamelCase'):
    expect(_common.format_label('CamelCaseWord')).to(equal('camel case word'))

  with it('converts snake_case'):
    expect(_common.format_label('snake_case_word')).to(equal('snake case word'))

with description('_common_spec.format_solution_html'):
  with it('wraps with pre tags'):
    expect(_common.preformat_html('foobar')).to(equal(
        '<pre>foobar</pre>'))

  with it('replaces newlines'):
    expect(_common.preformat_html('a\nb\nc')).to(equal(
        '<pre>a<br />b<br />c</pre>'))
