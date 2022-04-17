from typing import (
    Any,
    Iterable,
    TYPE_CHECKING,
)


if TYPE_CHECKING:
    from revy.abc.attribute_delta import AttributeDelta
    from revy.abc.delta import Delta
    from revy.abc.object_delta import ObjectDelta

__all__ = (
    'Revision',
)


class Revision:

    def get_description(self) -> str:
        raise NotImplementedError()

    def set_description(
        self,
        description: str,
    ) -> None:
        raise NotImplementedError()

    def get_deltas(self) -> Iterable['Delta']:
        raise NotImplementedError()

    def get_object_deltas(self) -> Iterable['ObjectDelta']:
        raise NotImplementedError()

    def get_attribute_deltas(self) -> Iterable['AttributeDelta']:
        raise NotImplementedError()

    def get_actors(self) -> Iterable[Any]:
        raise NotImplementedError()
