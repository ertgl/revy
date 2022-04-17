from contextlib import suppress
from typing import (
    Any,
    List,
    Type,
    cast,
)

from django.apps import apps
from django.db.models import Model

from revy.contrib.django.conf import settings
from revy.contrib.django.patcher import Patcher


__all__ = (
    'setup',
)


_PATCHED_MODELS: List[Type[Model]] = []


def setup(
    *args: Any,
    **kwargs: Any,
) -> None:
    setting = kwargs.get('setting', '')
    if setting and not setting.startswith('REVY_'):
        return
    for patched_model in _PATCHED_MODELS:
        Patcher.unpatch_model(patched_model)
    _PATCHED_MODELS.clear()
    is_revy_installed = False
    with suppress(LookupError):
        revy_app_config = apps.get_app_config('revy')
        is_revy_installed = revy_app_config is not None
    if not is_revy_installed:
        return
    models: List[Type[Model]] = []
    if '*' in settings.MODELS:
        models = apps.get_models(
            include_auto_created=settings.INCLUDE_AUTO_CREATED_MODELS,
        )
    else:
        for model_name in settings.MODELS:
            model = cast(Type[Model], apps.get_model(model_name))
            models.append(model)
    for model in models:
        Patcher.patch_model(model)
        _PATCHED_MODELS.append(model)
