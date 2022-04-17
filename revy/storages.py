import abc
from typing import (
    TYPE_CHECKING,
    Type,
)

import stackholm


if TYPE_CHECKING:
    from revy.context import Context


__all__ = (
    'Storage',
    'ASGIRefLocalStorage',
)


class Storage(
    stackholm.Storage,
    metaclass=abc.ABCMeta,
):

    @classmethod
    def get_base_context_class(cls) -> Type['Context']:
        from revy.context import Context
        return Context


class ASGIRefLocalStorage(
    Storage,
    stackholm.ASGIRefLocalStorage,
):
    ...
