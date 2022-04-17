from typing import (
    Any,
    Generic,
    Type,
    TypeVar,
    cast,
)


__all__ = (
    'mimic_generic',
)


T = TypeVar('T')


class _Generic(
    Generic[T],
):

    type_: Type[T]

    def __init__(
        self,
        type_: Type[T],
    ) -> None:
        self.type_ = type_

    def __getitem__(
        self,
        *args: Any,
    ) -> Type[T]:
        return self.type_


def mimic_generic(
    type_: Type[T],
) -> Type[T]:
    return cast(Type[T], _Generic(type_))
