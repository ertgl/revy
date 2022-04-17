from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
    Type,
    Union,
)

import stackholm

from revy.abc import (
    LazyRevision,
    Revision,
)


__all__ = (
    'ContextMeta',
    'Context',
)


class ContextMeta(type):

    def __new__(
        mcs,
        name: str,
        bases: Tuple[Type, ...],
        namespace: Dict[str, Any],
    ) -> type:
        if namespace.get('_storage') is None:
            from revy.globals import global_storage
            namespace['_storage'] = global_storage
        return super(ContextMeta, mcs).__new__(mcs, name, bases, namespace)


class Context(
    stackholm.Context,
    metaclass=ContextMeta,
):

    class Key:

        IS_DISABLED = 'is_disabled'

        REVISION = 'revision'

        REVISION_DESCRIPTION = 'revision_description'

        ACTOR = 'actor'

        OBJECT_DELTA_DESCRIPTION = 'object_delta_description'

        ATTRIBUTE_DELTA_DESCRIPTION = 'attribute_delta_description'

        DELETION_DESCRIPTION = 'deletion_description'

    @classmethod
    def via(
        cls,
        **kwargs: Any,
    ) -> 'Context':
        context = cls()
        context.checkpoint_data.update(kwargs)
        return context

    @classmethod
    def disable(cls) -> None:
        cls.set_checkpoint_value(cls.Key.IS_DISABLED, True)

    @classmethod
    def is_disabled(cls) -> bool:
        if cls.get_current() is None:
            return True
        if cls.get_checkpoint_value(cls.Key.IS_DISABLED, False):
            return True
        return False

    @classmethod
    def as_disabled(cls) -> 'Context':
        context = cls()
        context.checkpoint_data[cls.Key.IS_DISABLED] = True
        return context

    @classmethod
    def enable(cls) -> None:
        cls.pop_checkpoint_value(cls.Key.IS_DISABLED)

    @classmethod
    def is_enabled(cls) -> bool:
        return not cls.is_disabled()

    @classmethod
    def as_enabled(cls) -> 'Context':
        context = cls()
        context.checkpoint_data[cls.Key.IS_DISABLED] = False
        return context

    @classmethod
    def get_revision(cls) -> Optional[Revision]:
        revision = cls.get_checkpoint_value(cls.Key.REVISION)
        if isinstance(revision, LazyRevision):
            return revision()
        return revision

    @classmethod
    def set_revision(
        cls,
        revision: Union[
            None,
            Revision,
            LazyRevision,
        ],
    ) -> None:
        cls.set_checkpoint_value(
            cls.Key.REVISION,
            revision,
        )

    @classmethod
    def unset_revision(cls) -> None:
        cls.pop_checkpoint_value(cls.Key.REVISION)

    @classmethod
    def reset_revision(cls) -> None:
        cls.reset_checkpoint_value(cls.Key.REVISION)

    @classmethod
    def via_revision(
        cls,
        revision: Union[
            None,
            Revision,
            LazyRevision,
        ],
    ) -> 'Context':
        context = cls()
        context.checkpoint_data[cls.Key.REVISION] = revision
        return context

    @classmethod
    def get_revision_description(cls) -> str:
        return cls.get_checkpoint_value(cls.Key.REVISION_DESCRIPTION) or ''

    @classmethod
    def set_revision_description(
        cls,
        revision_description: Optional[str],
    ) -> None:
        cls.set_checkpoint_value(
            cls.Key.REVISION_DESCRIPTION,
            revision_description,
        )

    @classmethod
    def unset_revision_description(cls) -> None:
        cls.pop_checkpoint_value(cls.Key.REVISION_DESCRIPTION)

    @classmethod
    def reset_revision_description(cls) -> None:
        cls.reset_checkpoint_value(cls.Key.REVISION_DESCRIPTION)

    @classmethod
    def via_revision_description(
        cls,
        revision_description: Optional[str],
    ) -> 'Context':
        context = cls()
        context.checkpoint_data[cls.Key.REVISION_DESCRIPTION] = revision_description
        return context

    @classmethod
    def get_actor(cls) -> Optional[Any]:
        return cls.get_checkpoint_value(cls.Key.ACTOR)

    @classmethod
    def set_actor(
        cls,
        actor: Optional[Any],
    ) -> None:
        cls.set_checkpoint_value(cls.Key.ACTOR, actor)

    @classmethod
    def unset_actor(cls) -> None:
        cls.pop_checkpoint_value(cls.Key.ACTOR)

    @classmethod
    def reset_actor(cls) -> None:
        cls.reset_checkpoint_value(cls.Key.ACTOR)

    @classmethod
    def via_actor(
        cls,
        actor: Optional[Any],
    ) -> 'Context':
        context = cls()
        context.checkpoint_data[cls.Key.ACTOR] = actor
        return context

    @classmethod
    def get_object_delta_description(cls) -> str:
        return cls.get_checkpoint_value(cls.Key.OBJECT_DELTA_DESCRIPTION) or ''

    @classmethod
    def set_object_delta_description(
        cls,
        object_delta_description: Optional[str],
    ) -> None:
        cls.set_checkpoint_value(
            cls.Key.OBJECT_DELTA_DESCRIPTION,
            object_delta_description,
        )

    @classmethod
    def unset_object_delta_description(cls) -> None:
        cls.pop_checkpoint_value(cls.Key.OBJECT_DELTA_DESCRIPTION)

    @classmethod
    def reset_object_delta_description(cls) -> None:
        cls.reset_checkpoint_value(cls.Key.OBJECT_DELTA_DESCRIPTION)

    @classmethod
    def via_object_delta_description(
        cls,
        object_delta_description: Optional[str],
    ) -> 'Context':
        context = cls()
        context.checkpoint_data[cls.Key.OBJECT_DELTA_DESCRIPTION] = object_delta_description
        return context

    @classmethod
    def get_attribute_delta_description(cls) -> str:
        return cls.get_checkpoint_value(cls.Key.ATTRIBUTE_DELTA_DESCRIPTION) or ''

    @classmethod
    def set_attribute_delta_description(
        cls,
        attribute_delta_description: Optional[str],
    ) -> None:
        cls.set_checkpoint_value(
            cls.Key.ATTRIBUTE_DELTA_DESCRIPTION,
            attribute_delta_description,
        )

    @classmethod
    def unset_attribute_delta_description(cls) -> None:
        cls.pop_checkpoint_value(cls.Key.ATTRIBUTE_DELTA_DESCRIPTION)

    @classmethod
    def reset_attribute_delta_description(cls) -> None:
        cls.reset_checkpoint_value(cls.Key.ATTRIBUTE_DELTA_DESCRIPTION)

    @classmethod
    def via_attribute_delta_description(
        cls,
        attribute_delta_description: Optional[str],
    ) -> 'Context':
        context = cls()
        context.checkpoint_data[cls.Key.ATTRIBUTE_DELTA_DESCRIPTION] = attribute_delta_description
        return context

    @classmethod
    def get_deletion_description(cls) -> str:
        return cls.get_checkpoint_value(cls.Key.DELETION_DESCRIPTION) or ''

    @classmethod
    def set_deletion_description(
        cls,
        deletion_description: Optional[str],
    ) -> None:
        cls.set_checkpoint_value(
            cls.Key.DELETION_DESCRIPTION,
            deletion_description,
        )

    @classmethod
    def unset_deletion_description(cls) -> None:
        cls.pop_checkpoint_value(cls.Key.DELETION_DESCRIPTION)

    @classmethod
    def reset_deletion_description(cls) -> None:
        cls.reset_checkpoint_value(cls.Key.DELETION_DESCRIPTION)

    @classmethod
    def via_deletion_description(
        cls,
        deletion_description: Optional[str],
    ) -> 'Context':
        context = cls()
        context.checkpoint_data[cls.Key.DELETION_DESCRIPTION] = deletion_description
        return context
