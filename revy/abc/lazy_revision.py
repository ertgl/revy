from typing import (
    Optional,
    Protocol,
    runtime_checkable,
)

from revy.abc.revision import Revision


__all__ = (
    'LazyRevision',
)


@runtime_checkable
class LazyRevision(Protocol):

    def __call__(self) -> Optional[Revision]:
        ...
