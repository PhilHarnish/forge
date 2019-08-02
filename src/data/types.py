from typing import Any, Callable, Optional, Tuple, Union

from rx import subjects

Observer = Union[subjects.Subject, Callable[[Any], None]]
Path = Optional[Tuple[str, 'Path']]
WeightedWord = Tuple[str, float]
