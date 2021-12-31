import re
from typing import List

_OPTION = re.compile(
    r'^'
    r'(?:(?P<relation>Either|Neither|Exactly one of) )?(?:answers?) '
    r'(?P<options>.*) '
    r'(?P<assertion>(?:is|are)(?: not)?) '
    r'(?:both )?'
    r'(?P<value>(?:in)?correct)(?: \(possibly both\))?'
    r'\.$',
    re.IGNORECASE,
)
_OPTION_SPLIT = re.compile(r' (?:and|or|nor answer) ')


class _Option(object):
  def __init__(self, option:str, line: str) -> None:
    match = _OPTION.match(line.lower())
    if not match:
      raise NotImplementedError(line)
    self._option = option
    self._line = line

    result = match.groupdict()
    self._variables = tuple(map(
        str.upper, _OPTION_SPLIT.split(result['options'])))
    self._relation = result['relation']
    self._assertion = result['assertion']
    self._value = result['value']

  def _condition(self) -> str:
    expression = self._expression()
    if ' ' in expression:
      expression = '(%s)' % expression
    if self._value == 'correct':
      return expression
    return '(not %s)' % expression

  def _expression(self) -> str:
    if not self._relation:
      cond = ' & '.join(self._variables)
      if self._assertion in ('is', 'are'):
        return cond
      elif self._assertion == 'are not':
        return 'not (%s)' % cond
    elif self._relation == 'exactly one of' and len(self._variables) == 2:
      return ' != '.join(self._variables)
    elif self._relation == 'either':
      return ' | '.join(self._variables)
    elif self._relation == 'neither':
      return ' & '.join('(not %s)' % v for v in self._variables)
    raise NotImplementedError(self._line)

  def __str__(self) -> str:
    return '%s == %s  # %s' % (
      self._option,  # Option == ...
      self._condition(),
      self._line,  # Comment.
    )


class Question(object):
  def __init__(self, options: List[_Option]) -> None:
    self._options = options

  def variables(self) -> List[str]:
    return [chr(ord('A') + i) for i in range(len(self._options))]

  def __str__(self) -> str:
    return '\n'.join(str(option) for option in self._options)


def parse_questions(text: str) -> List[Question]:
  acc = []
  result = []
  for line in _clean_split(text):
    if line.endswith('?'):
      acc = []
      result.append(Question(acc))
    else:
      acc.append(parse_option('ABCDE'[len(acc)], line))
  return result


def parse_option(option: str, line: str) -> _Option:
  return _Option(option, line)


def _clean_split(text: str) -> List[str]:
  return text.strip().split('\n')
