import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

import revy
import revy.contrib.django.models


class Account(models.Model):

    code = models.CharField(  # type: ignore
        max_length=255,
        blank=False,
        null=False,
        unique=True,
    )


class Transaction(models.Model):

    TYPE_DEBIT = 'Debit'

    TYPE_CREDIT = 'Credit'

    TYPE_CHOICES = (
        (TYPE_DEBIT, _('Debit')),
        (TYPE_CREDIT, _('Credit')),
    )

    account = models.ForeignKey(  # type: ignore
        Account,
        on_delete=revy.contrib.django.models.CASCADE,
    )

    type = models.CharField(  # type: ignore
        max_length=255,
        blank=False,
        null=False,
        choices=TYPE_CHOICES,
    )

    amount = models.DecimalField(  # type: ignore
        max_digits=20,
        decimal_places=2,
        blank=False,
        null=False,
    )

    iso_4217_code = models.CharField(  # type: ignore
        max_length=3,
        blank=False,
        null=False,
    )

    exchange_rate = models.DecimalField(  # type: ignore
        max_digits=20,
        decimal_places=2,
        blank=False,
        null=False,
        default=1,
    )

    local_amount = models.DecimalField(  # type: ignore
        max_digits=20,
        decimal_places=2,
        blank=False,
        null=False,
    )

    date = models.DateField(  # type: ignore
        blank=False,
        null=False,
        default=datetime.date.today,
    )

    @revy.Context.via_actor(None)
    def clean(self) -> None:
        local_amount = round(self.amount * self.exchange_rate, 2)
        if self.local_amount != local_amount:
            with revy.Context.via_attribute_delta_description('Corrected by system.'):
                self.local_amount = local_amount
