from typing import (
    Any,
    Optional,
)

from revy.abc.delta import Delta
from revy.abc.object_delta import ObjectDelta


__all__ = (
    'AttributeDelta',
)


class AttributeDelta(Delta):  # noqa

    def get_object_delta(self) -> ObjectDelta:
        raise NotImplementedError()

    def set_object_delta(
        self,
        object_delta: ObjectDelta,
    ) -> None:
        raise NotImplementedError()

    def get_attribute_name(self) -> str:
        raise NotImplementedError()

    def set_attribute_name(
        self,
        attribute_name: str,
    ) -> None:
        raise NotImplementedError()

    def get_old_value(self) -> Optional[Any]:
        raise NotImplementedError()

    def set_old_value(
        self,
        old_value: Optional[Any],
    ) -> None:
        raise NotImplementedError()

    def get_new_value(self) -> Optional[Any]:
        raise NotImplementedError()

    def set_new_value(
        self,
        new_value: Optional[Any],
    ) -> None:
        raise NotImplementedError()
