"""
Constraints validate value matches specified type before assigning.

Constraints are:
* Optional or required
* May have one or more values
"""
import contextlib
import re
import textwrap
from typing import Any, Dict, Generic, Iterable, Iterator, NamedTuple, \
  Optional, \
  Tuple, Union

from rx import subjects

from data import types
from puzzle.constraints import validator

Constraint = Union[validator.Validator, type]


class ConstraintSpec(NamedTuple):
  name: str
  value: Any
  annotation: type
  docs: Optional[str]


class ConstraintChangeEvent(NamedTuple):
  """Fired when `key` of `constraints` changes from `previous` to `current`."""
  constraints: 'Constraints'
  key: Optional[str]
  previous: Any
  current: Any
  queued: Optional['ConstraintChangeEvent']  # Last unflushed event.


# Find penultimate class from typing module. ("object" is final base class.)
_TYPING_BASES = (type(Union).mro()[-2], Generic)
# Matches `constraint_name: ...` but not `Some text: the sequel`.
_CONSTRAINT_RE = re.compile(r'^([a-z_]+):(.*)$')


class Constraints(object):
  _subject: subjects.Subject = None
  _ordered_keys: Iterable[str] = ()
  _paused_broadcast: int = 0
  _queued: Optional[ConstraintChangeEvent] = None
  _docs: Dict[str, str] = None

  def __init__(self) -> None:
    self._subject = subjects.Subject()
    self._paused_broadcast = 0
    self._queued = None
    self._docs = _parse_docs(self.__class__.__doc__)

  def subscribe(self, observer: types.Observer):
    self._subject.subscribe(observer)

  def is_modifiable(self, key: str) -> bool:
    del key
    return True

  def __iter__(self) -> Iterable[ConstraintSpec]:
    for key in self.__dir__():  # NOTE: dir(...) returns sorted results.
      if self._is_internal(key):
        continue
      annotation = self._resolve_annotation(key)
      if annotation:
        yield key, getattr(self, key), annotation, self._resolve_docs(key)

  def __setattr__(self, key: str, value: Any) -> None:
    if self._is_internal(key):
      object.__setattr__(self, key, value)
      return
    annotation = self._resolve_annotation(key)
    if not annotation:
      raise AttributeError('%s not in %s' % (key, self.__class__.__name__))
    if not _type_check(value, annotation):
      raise ValueError('%s.%s must be %s (%s given)' % (
          self.__class__.__name__, key, annotation, value,
      ))
    if not self.is_modifiable(key):
      raise AttributeError('%s is not modifiable' % key)
    previous = object.__getattribute__(self, key)
    if previous != value:
      object.__setattr__(self, key, value)
      self._queued = ConstraintChangeEvent(
          self, key, previous, value, self._queued)
      self._before_change_event(self._queued)
      if not self._paused_broadcast:
        self._flush()

  def __repr__(self) -> str:
    return '%s()' % self.__class__.__name__

  def __str__(self) -> str:
    results = []
    for key, value, _, docs in self:
      if docs:
        results.append('%s = %s  # %s' % (key, repr(value), docs))
      else:
        results.append('%s = %s' % (key, repr(value)))
    return '\n'.join(results)

  def __dir__(self) -> Iterable[str]:
    superset = set(super().__dir__())
    for key in self._ordered_keys:
      yield key
      superset.remove(key)
    for key in sorted(superset):
      yield key

  def _is_internal(self, key: str) -> bool:
    if not hasattr(self, key):
      raise AttributeError('%s not in %s' % (key, self.__class__.__name__))
    return key.startswith('_')  # Hide private properties.

  @contextlib.contextmanager
  def _pause_events(self, flush: bool = False) -> Iterator[None]:
    self._paused_broadcast += 1
    yield
    self._paused_broadcast -= 1
    if flush:
      self._flush()

  def _flush(self) -> None:
    if self._queued:
      self._subject.on_next(self._queued)
      self._queued = None

  def _before_change_event(self, event: ConstraintChangeEvent) -> None:
    del event  # Unused.

  def _resolve_annotation(self, key: str) -> Optional[type]:
    return _resolve_annotation(self.__class__, key)

  def _resolve_docs(self, key: str) -> Optional[str]:
    return self._docs.get(key)


def unwrap_optional(annotation: type) -> Optional[type]:
  if (not isinstance(annotation, type(Union)) or
      not hasattr(annotation, '__args__')):
    return None
  args = getattr(annotation, '__args__')
  if len(args) != 2:
    return None
  return next(a for a in args if a is not type(None))  # First non-None value.


def _type_check(value: Any, annotation: type) -> bool:
  if (not isinstance(annotation, _TYPING_BASES) or
      not hasattr(annotation, '__args__')):
    return isinstance(value, annotation)
  args = getattr(annotation, '__args__')  # E.g. "a, b, c" in Union[a, b, c].
  if isinstance(annotation, type(Union)):
    # With Union, any of the arguments are valid.
    # NB: `Optional` is an alias for Union.
    return any(_type_check(value, a) for a in args)
  elif isinstance(annotation, type(Tuple)):
    return isinstance(value, tuple) and len(value) == len(args) and all(
        _type_check(v, a) for v, a in zip(value, args))
  elif isinstance(annotation, type(Iterable)):
    if (hasattr(annotation, '__extra__') and
        not isinstance(value, getattr(annotation, '__extra__'))):
      return False  # E.g., __extra__ is `list` for typing.List.
    try:
      sample_value = next(iter(value))
      return any(_type_check(sample_value, a) for a in args)
    except TypeError:
      return False
  return False


def _resolve_annotation(cls: type, k: str) -> Optional[type]:
  for klass in cls.mro():
    if not hasattr(klass, '__annotations__') or k not in klass.__annotations__:
      continue
    return klass.__annotations__[k]
  return None


def _parse_docs(docs: Optional[str]) -> Dict[str, str]:
  if not docs:
    return {}
  if docs.startswith(' '):
    first_line = ''
  else:
    # Sometimes the class has 1 line of documentation to ignore.
    first_line, docs = docs.split('\n', 1)
  docs = textwrap.dedent(docs)
  if first_line:
    docs = first_line + '\n' + docs
  result = {}
  buffer = []
  name = None
  for line in docs.split('\n'):
    has_name = _CONSTRAINT_RE.match(line)
    if has_name:
      if name:
        result[name] = ' '.join(buffer)
        buffer.clear()
      name = has_name.group(1)
      buffer.append(has_name.group(2).strip())
    elif name:
      buffer.append(line.strip())
  if name:
    result[name] = ' '.join(buffer)
  return result
