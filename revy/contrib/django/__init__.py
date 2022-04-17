from revy.contrib.django.setup import setup
from revy.contrib.django.utils import (
    get_attribute_delta_model,
    get_delta_model,
    get_object_delta_model,
    get_revision_model,
)


__all__ = (
    'setup',
    'get_revision_model',
    'get_delta_model',
    'get_object_delta_model',
    'get_attribute_delta_model',
)
