from typing import Any

from revy.abc.revision import Revision


__all__ = (
    'Delta',
)


class Delta:

    def get_revision(self) -> Revision:
        raise NotImplementedError()

    def set_revision(
        self,
        revision: Revision,
    ) -> None:
        raise NotImplementedError()

    def get_actor(self) -> Any:
        raise NotImplementedError()

    def set_actor(
        self,
        actor: Any
    ) -> None:
        raise NotImplementedError()

    def get_action(self) -> str:
        raise NotImplementedError()

    def set_action(
        self,
        action: str
    ) -> None:
        raise NotImplementedError()

    def get_object(self) -> Any:
        raise NotImplementedError()

    def set_object(
        self,
        object_: Any,
    ) -> None:
        raise NotImplementedError()

    def get_description(self) -> str:
        raise NotImplementedError()

    def set_description(
        self,
        description: str
    ) -> None:
        raise NotImplementedError()
