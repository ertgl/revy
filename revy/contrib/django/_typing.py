from typing import TYPE_CHECKING

from django.db import models

from revy.contrib.django._typing_ext import mimic_generic


__all__ = (
    'IS_MYPY_DJANGO_PLUGIN_ENABLED',
    'CharField',
    'TextField',
    'DateTimeField',
    'ForeignKey',
    'OneToOneField',
    'QuerySet',
)


IS_MYPY_DJANGO_PLUGIN_ENABLED = False

try:
    import mypy_django_plugin  # noqa
    try:
        if TYPE_CHECKING:
            models.Field[object, object]  # noqa
            IS_MYPY_DJANGO_PLUGIN_ENABLED = True
    except TypeError:
        IS_MYPY_DJANGO_PLUGIN_ENABLED = False
except ImportError:
    IS_MYPY_DJANGO_PLUGIN_ENABLED = False


CharField = models.CharField
if not TYPE_CHECKING or not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    CharField = mimic_generic(models.CharField)  # type: ignore[misc]


TextField = models.TextField
if not TYPE_CHECKING or not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    TextField = mimic_generic(models.TextField)  # type: ignore[misc]


DateTimeField = models.DateTimeField
if not TYPE_CHECKING or not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    DateTimeField = mimic_generic(models.DateTimeField)  # type: ignore[misc]


ForeignKey = models.ForeignKey
if not TYPE_CHECKING or not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    ForeignKey = mimic_generic(models.ForeignKey)  # type: ignore[misc]


OneToOneField = models.OneToOneField
if not TYPE_CHECKING or not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    OneToOneField = mimic_generic(models.OneToOneField)  # type: ignore[misc]


QuerySet = models.QuerySet
if not TYPE_CHECKING or not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    QuerySet = mimic_generic(models.QuerySet)  # type: ignore[misc]
