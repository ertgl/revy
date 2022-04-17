from typing import (
    Any,
    Type,
)

from django.apps import AppConfig
from django.db.models import (
    Model,
    signals,
)


class LedgerConfig(AppConfig):

    name = 'ledger'

    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self) -> None:

        def validate(
            sender: Type[Model],
            instance: Model,
            **kwargs: Any,
        ) -> None:
            instance.clean()

        signals.pre_save.connect(validate, dispatch_uid='ledger.validate')
