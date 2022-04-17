from django.conf import settings
from django.db import models

from revy.contrib.django import models as revy_models


class Revision(
    revy_models.BaseRevision,
    models.Model,
):

    class Meta:
        ...


class Delta(
    revy_models.BaseDelta,
    models.Model,
):

    class Meta:
        ...


class ObjectDelta(
    revy_models.BaseObjectDelta,
    Delta,
):

    object_delta_ptr = models.OneToOneField(  # type: ignore
        verbose_name='delta pointer',
        to=settings.REVY_DELTA_MODEL,
        on_delete=models.CASCADE,
        related_name='object_delta',
        related_query_name='object_delta',
        parent_link=True,
    )

    class Meta:
        ...


class AttributeDelta(
    revy_models.BaseAttributeDelta,
    Delta,
):

    attribute_delta_ptr = models.OneToOneField(  # type: ignore
        verbose_name='delta pointer',
        to=settings.REVY_DELTA_MODEL,
        on_delete=models.CASCADE,
        related_name='attribute_delta',
        related_query_name='attribute_delta',
        parent_link=True,
    )

    class Meta:
        ...
