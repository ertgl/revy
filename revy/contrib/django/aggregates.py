from typing import (
    Any,
    TYPE_CHECKING,
    Type,
    TypeVar,
    cast,
)

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import (
    Field,
    JSONField,
    Model,
    OuterRef,
    Subquery,
)
from django.db.models.functions import JSONObject  # type: ignore[attr-defined]
from django.db.models.functions import Cast
from django.db.models.options import Options

from revy.contrib.django.utils import (
    get_attribute_delta_model,
    get_object_delta_model,
)


if TYPE_CHECKING:
    from revy.contrib.django.models import AbstractDelta


__all__ = ("ObjectSnapshot",)


T = TypeVar("T")


class _InstanceField(JSONField):
    model: Type[Model]

    def __init__(
        self,
        model: Type[Model],
        **kwargs: Any,
    ) -> None:
        self.model = model
        super(_InstanceField, self).__init__(**kwargs)

    def from_db_value(
        self,
        value: Any,
        expression: Any,
        connection: BaseDatabaseWrapper,
    ) -> Any:
        python_value = super(_InstanceField, self).from_db_value(  # type: ignore[misc]
            value,
            expression,
            connection,
        )
        if isinstance(python_value, dict):
            return self.model(**python_value)
        if isinstance(python_value, (list, tuple)):
            container_type = type(python_value)
            return container_type(
                map(lambda kwargs: self.model(**kwargs), python_value)
            )
        return python_value


class ObjectSnapshot(Subquery):
    @classmethod
    def get_ct_fk_fields(
        cls,
        delta_model: Type["AbstractDelta"],
    ) -> tuple[Field, Field]:
        options = cast(Options, delta_model._meta)  # noqa
        generic_fk_field = cast(
            GenericForeignKey,
            options.get_field(delta_model.OBJECT_FIELD_NAME),
        )
        ct_field = cast(Field, options.get_field(generic_fk_field.ct_field))
        fk_field = cast(Field, options.get_field(generic_fk_field.fk_field))
        return ct_field, fk_field

    @classmethod
    def build_json_object(
        cls,
        model: Type[Model],
    ) -> JSONObject:
        object_delta_model = get_object_delta_model()
        attribute_delta_model = get_attribute_delta_model()
        annotations = dict()
        options = cast(Options, model._meta)  # noqa
        obj_ct_field, obj_fk_field = cls.get_ct_fk_fields(object_delta_model)
        att_ct_field, att_fk_field = cls.get_ct_fk_fields(attribute_delta_model)
        for field in options.get_fields():
            attname = getattr(field, "attname", None)
            one_to_many = getattr(field, "one_to_many", False)
            many_to_many = getattr(field, "many_to_many", False)
            any_to_many = one_to_many or many_to_many
            if not attname or any_to_many:
                continue
            annotations[attname] = (
                attribute_delta_model.objects.filter(
                    **{
                        att_ct_field.attname: OuterRef(obj_ct_field.attname),
                        att_fk_field.attname: OuterRef(obj_fk_field.attname),
                        attribute_delta_model.ATTRIBUTE_NAME_FIELD_NAME: attname,
                        f"{attribute_delta_model.OBJECT_DELTA_FIELD_NAME}__pk__lte": OuterRef(
                            "pk"
                        ),
                    },
                )
                .order_by(
                    "-pk",
                )
                .values(
                    attribute_delta_model.NEW_VALUE_FIELD_NAME,
                )[:1]
            )
        return JSONObject(**annotations)  # type: ignore[arg-type]

    @classmethod
    def build_instance(
        cls,
        model: Type[Model],
    ) -> Cast:
        return Cast(cls.build_json_object(model), output_field=_InstanceField(model))

    def __init__(
        self,
        model: Type[Model],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        object_delta_model = get_object_delta_model()
        queryset = (
            object_delta_model.objects.filter(
                pk=OuterRef("pk"),
            )
            .annotate(
                snapshot=self.__class__.build_instance(model),
            )
            .values(
                "snapshot",
            )[:1]
        )
        super(ObjectSnapshot, self).__init__(queryset, **kwargs)
