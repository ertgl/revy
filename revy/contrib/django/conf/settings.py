from typing import Sequence

from django.conf import settings


__all__ = (
    'MODELS_ATTNAME',
    'DEFAULT_MODELS',
    'MODELS',
    'REVISION_MODEL_ATTNAME',
    'DEFAULT_REVISION_MODEL',
    'REVISION_MODEL',
    'INCLUDE_AUTO_CREATED_MODELS_ATTNAME',
    'DEFAULT_INCLUDE_AUTO_CREATED_MODELS',
    'INCLUDE_AUTO_CREATED_MODELS',
    'REVISION_MODEL_ATTNAME',
    'DEFAULT_REVISION_MODEL',
    'REVISION_MODEL',
    'DELTA_MODEL_ATTNAME',
    'DEFAULT_DELTA_MODEL',
    'DELTA_MODEL',
    'OBJECT_DELTA_MODEL_ATTNAME',
    'DEFAULT_OBJECT_DELTA_MODEL',
    'OBJECT_DELTA_MODEL',
    'ATTRIBUTE_DELTA_MODEL_ATTNAME',
    'DEFAULT_ATTRIBUTE_DELTA_MODEL',
    'ATTRIBUTE_DELTA_MODEL',
    'JSON_ENCODER_CLASS_ATTNAME',
    'DEFAULT_JSON_ENCODER_CLASS',
    'JSON_ENCODER_CLASS',
    'DELETION_ITERATOR_CHUNK_SIZE_ATTNAME',
    'DEFAULT_DELETION_ITERATOR_CHUNK_SIZE',
    'DELETION_ITERATOR_CHUNK_SIZE',
    'CONTEXT_CLASS_ATTNAME',
    'DEFAULT_CONTEXT_CLASS',
    'CONTEXT_CLASS',
)


MODELS_ATTNAME = 'REVY_MODELS'

DEFAULT_MODELS = ('*',)

MODELS: Sequence[str]


INCLUDE_AUTO_CREATED_MODELS_ATTNAME = 'REVY_INCLUDE_AUTO_CREATED_MODELS'

DEFAULT_INCLUDE_AUTO_CREATED_MODELS = True

INCLUDE_AUTO_CREATED_MODELS: bool


REVISION_MODEL_ATTNAME = 'REVY_REVISION_MODEL'

DEFAULT_REVISION_MODEL = 'revy.Revision'

REVISION_MODEL: str


DELTA_MODEL_ATTNAME = 'REVY_DELTA_MODEL'

DEFAULT_DELTA_MODEL = 'revy.Delta'

DELTA_MODEL: str


OBJECT_DELTA_MODEL_ATTNAME = 'REVY_OBJECT_DELTA_MODEL'

DEFAULT_OBJECT_DELTA_MODEL = 'revy.ObjectDelta'

OBJECT_DELTA_MODEL: str


ATTRIBUTE_DELTA_MODEL_ATTNAME = 'REVY_ATTRIBUTE_DELTA_MODEL'

DEFAULT_ATTRIBUTE_DELTA_MODEL = 'revy.AttributeDelta'

ATTRIBUTE_DELTA_MODEL: str


JSON_ENCODER_CLASS_ATTNAME = 'REVY_JSON_ENCODER_CLASS'

DEFAULT_JSON_ENCODER_CLASS = 'django.core.serializers.json.DjangoJSONEncoder'

JSON_ENCODER_CLASS: str


DELETION_ITERATOR_CHUNK_SIZE_ATTNAME = 'REVY_DELETION_ITERATOR_CHUNK_SIZE'

DEFAULT_DELETION_ITERATOR_CHUNK_SIZE = 1000

DELETION_ITERATOR_CHUNK_SIZE: int


CONTEXT_CLASS_ATTNAME = 'REVY_CONTEXT_CLASS'

DEFAULT_CONTEXT_CLASS = 'revy.Context'

CONTEXT_CLASS: str


def reload() -> None:
    global MODELS
    MODELS = getattr(
        settings,
        MODELS_ATTNAME,
        (),
    ) or DEFAULT_MODELS
    if not hasattr(settings, MODELS_ATTNAME):
        setattr(settings, MODELS_ATTNAME, MODELS)

    global INCLUDE_AUTO_CREATED_MODELS
    INCLUDE_AUTO_CREATED_MODELS = getattr(
        settings,
        INCLUDE_AUTO_CREATED_MODELS_ATTNAME,
        DEFAULT_INCLUDE_AUTO_CREATED_MODELS,
    )
    if not hasattr(settings, INCLUDE_AUTO_CREATED_MODELS_ATTNAME):
        setattr(settings, INCLUDE_AUTO_CREATED_MODELS_ATTNAME, INCLUDE_AUTO_CREATED_MODELS)

    global REVISION_MODEL
    REVISION_MODEL = getattr(
        settings,
        REVISION_MODEL_ATTNAME,
        None,
    ) or DEFAULT_REVISION_MODEL
    if not hasattr(settings, REVISION_MODEL_ATTNAME):
        setattr(settings, REVISION_MODEL_ATTNAME, REVISION_MODEL)

    global DELTA_MODEL
    DELTA_MODEL = getattr(
        settings,
        DELTA_MODEL_ATTNAME,
        None,
    ) or DEFAULT_DELTA_MODEL
    if not hasattr(settings, DELTA_MODEL_ATTNAME):
        setattr(settings, DELTA_MODEL_ATTNAME, DELTA_MODEL)

    global OBJECT_DELTA_MODEL
    OBJECT_DELTA_MODEL = getattr(
        settings,
        OBJECT_DELTA_MODEL_ATTNAME,
        None,
    ) or DEFAULT_OBJECT_DELTA_MODEL
    if not hasattr(settings, OBJECT_DELTA_MODEL_ATTNAME):
        setattr(settings, OBJECT_DELTA_MODEL_ATTNAME, OBJECT_DELTA_MODEL)

    global ATTRIBUTE_DELTA_MODEL
    ATTRIBUTE_DELTA_MODEL = getattr(
        settings,
        ATTRIBUTE_DELTA_MODEL_ATTNAME,
        None,
    ) or DEFAULT_ATTRIBUTE_DELTA_MODEL
    if not hasattr(settings, ATTRIBUTE_DELTA_MODEL_ATTNAME):
        setattr(settings, ATTRIBUTE_DELTA_MODEL_ATTNAME, ATTRIBUTE_DELTA_MODEL)

    global JSON_ENCODER_CLASS
    JSON_ENCODER_CLASS = getattr(
        settings,
        JSON_ENCODER_CLASS_ATTNAME,
        None,
    ) or DEFAULT_JSON_ENCODER_CLASS
    if not hasattr(settings, JSON_ENCODER_CLASS_ATTNAME):
        setattr(settings, JSON_ENCODER_CLASS_ATTNAME, JSON_ENCODER_CLASS)

    global DELETION_ITERATOR_CHUNK_SIZE
    DELETION_ITERATOR_CHUNK_SIZE = getattr(
        settings,
        DELETION_ITERATOR_CHUNK_SIZE_ATTNAME,
        None,
    ) or DEFAULT_DELETION_ITERATOR_CHUNK_SIZE
    if not hasattr(settings, DELETION_ITERATOR_CHUNK_SIZE_ATTNAME):
        setattr(settings, DELETION_ITERATOR_CHUNK_SIZE_ATTNAME, DELETION_ITERATOR_CHUNK_SIZE)

    global CONTEXT_CLASS
    CONTEXT_CLASS = getattr(
        settings,
        CONTEXT_CLASS_ATTNAME,
        None,
    ) or DEFAULT_CONTEXT_CLASS
    if not hasattr(settings, CONTEXT_CLASS_ATTNAME):
        setattr(settings, CONTEXT_CLASS_ATTNAME, CONTEXT_CLASS)


reload()
