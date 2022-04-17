from typing import (
    Any,
    Iterable,
    TYPE_CHECKING,
)

from revy.abc.delta import Delta


if TYPE_CHECKING:
    from revy.abc.attribute_delta import AttributeDelta


__all__ = (
    'ObjectDelta',
)


class ObjectDelta(Delta):  # noqa

    def get_actors(self) -> Iterable[Any]:
        raise NotImplementedError()

    def get_attribute_deltas(self) -> Iterable['AttributeDelta']:
        raise NotImplementedError()
