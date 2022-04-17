from django.apps import AppConfig
from django.core.signals import setting_changed


__all__ = (
    'RevyConfig',
)


class RevyConfig(AppConfig):

    name = 'revy.contrib.django'

    verbose_name = 'Revy'

    label = 'revy'

    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self) -> None:
        from revy.contrib.django import setup
        setup()

        setting_changed.connect(
            setup,
            dispatch_uid='revy.contrib.django.setup',
        )
