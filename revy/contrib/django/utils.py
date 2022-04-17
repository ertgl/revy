from json import JSONEncoder
from typing import (
    TYPE_CHECKING,
    Type,
    cast,
)

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.utils.module_loading import import_string


if TYPE_CHECKING:
    from revy.contrib.django.models import (
        AbstractAttributeDelta,
        AbstractDelta,
        AbstractObjectDelta,
        AbstractRevision,
    )


__all__ = (
    'get_revision_model',
    'get_delta_model',
    'get_object_delta_model',
    'get_attribute_delta_model',
    'get_json_encoder_class',
)


def _get_swappable_model(
    setting_attname: str,
    model_class_path: str,
) -> Type[Model]:
    model: Type[Model]
    try:
        model = cast(
            Type[Model],
            apps.get_model(
                model_class_path,
                require_ready=False,
            ),
        )
    except ValueError:
        raise ImproperlyConfigured(
            f"{setting_attname} must be of the form 'app_label.model_name'",
        )
    except LookupError:
        raise ImproperlyConfigured(
            f"{setting_attname} refers to model '{model_class_path}' that has not been installed"
        )
    return model


def get_revision_model() -> Type['AbstractRevision']:
    from revy.contrib.django.conf import settings
    return cast(
        Type['AbstractRevision'],
        _get_swappable_model(
            settings.REVISION_MODEL_ATTNAME,
            settings.REVISION_MODEL,
        ),
    )


def get_delta_model() -> Type['AbstractDelta']:
    from revy.contrib.django.conf import settings
    return cast(
        Type['AbstractDelta'],
        _get_swappable_model(
            settings.DELTA_MODEL_ATTNAME,
            settings.DELTA_MODEL,
        ),
    )


def get_object_delta_model() -> Type['AbstractObjectDelta']:
    from revy.contrib.django.conf import settings
    return cast(
        Type['AbstractObjectDelta'],
        _get_swappable_model(
            settings.OBJECT_DELTA_MODEL_ATTNAME,
            settings.OBJECT_DELTA_MODEL,
        ),
    )


def get_attribute_delta_model() -> Type['AbstractAttributeDelta']:
    from revy.contrib.django.conf import settings
    return cast(
        Type['AbstractAttributeDelta'],
        _get_swappable_model(
            settings.ATTRIBUTE_DELTA_MODEL_ATTNAME,
            settings.ATTRIBUTE_DELTA_MODEL,
        ),
    )


def get_json_encoder_class() -> Type[JSONEncoder]:
    from revy.contrib.django.conf import settings
    return cast(
        Type[JSONEncoder],
        import_string(settings.JSON_ENCODER_CLASS),
    )
