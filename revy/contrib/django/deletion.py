from typing import (
    Any,
    Callable,
    Iterator,
    Optional,
)

from django.db.models import (
    Model,
    QuerySet,
)
from django.db.models.deletion import (
    CASCADE as _CASCADE,
    Collector,
    SET as _SET,
    SET_DEFAULT as _SET_DEFAULT,
    SET_NULL as _SET_NULL,
)
from django.db.models.fields.related import RelatedField

from revy import Context
from revy.contrib.django.conf import settings


__all__ = (
    'CASCADE',
    'SET',
    'SET_NULL',
    'SET_DEFAULT',
)


def _get_sub_object_iterator(
    sub_objects: QuerySet,
) -> Iterator[Model]:
    return sub_objects.iterator(
        chunk_size=settings.DELETION_ITERATOR_CHUNK_SIZE,
    )


def CASCADE(  # noqa
    collector: Collector,
    field: RelatedField,
    sub_objects: QuerySet,
    using: str,
) -> None:

    if Context.is_disabled():
        return _CASCADE(collector, field, sub_objects, using)

    with Context.via_actor(None):
        sub_object_iterator = _get_sub_object_iterator(sub_objects)
        for sub_object in sub_object_iterator:
            with Context.via_object_delta_description(
                Context.get_deletion_description(),
            ):
                sub_object.delete(using=using)


def SET(  # noqa
    value: Optional[Any],
) -> Callable[
    [Collector, RelatedField, QuerySet, str],
    None,
]:

    def set_on_delete(
        collector: Collector,
        field: RelatedField,
        sub_objects: QuerySet,
        using: str,
    ) -> None:

        if Context.is_disabled():
            return _SET(value)(collector, field, sub_objects, using)

        new_value = value
        if callable(new_value):
            new_value = new_value()

        with Context.via_actor(None):
            sub_object_iterator = _get_sub_object_iterator(sub_objects)
            for sub_object in sub_object_iterator:
                with Context.via_attribute_delta_description(
                    Context.get_deletion_description(),
                ):
                    setattr(sub_object, field.attname, new_value)
                sub_object.save(using=using)

    setattr(
        set_on_delete,
        'deconstruct',
        lambda: ('revy.contrib.django.models.SET', (value,), {}),
    )

    return set_on_delete


def SET_NULL(  # noqa
    collector: Collector,
    field: RelatedField,
    sub_objects: QuerySet,
    using: str,
) -> None:

    if Context.is_disabled():
        return _SET_NULL(collector, field, sub_objects, using)

    with Context.via_actor(None):
        sub_object_iterator = _get_sub_object_iterator(sub_objects)
        for sub_object in sub_object_iterator:
            with Context.via_attribute_delta_description(
                Context.get_deletion_description(),
            ):
                setattr(sub_object, field.attname, None)
            sub_object.save(using=using)


def SET_DEFAULT(  # noqa
    collector: Collector,
    field: RelatedField,
    sub_objects: QuerySet,
    using: str,
) -> None:

    if Context.is_disabled():
        return _SET_DEFAULT(collector, field, sub_objects, using)

    with Context.via_actor(None):
        sub_object_iterator = _get_sub_object_iterator(sub_objects)
        for sub_object in sub_object_iterator:
            with Context.via_attribute_delta_description(
                Context.get_deletion_description(),
            ):
                setattr(sub_object, field.attname, field.get_default())
            sub_object.save(using=using)
