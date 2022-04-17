from collections import defaultdict
import dataclasses
import datetime
from typing import (
    Any,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Protocol,
    Set,
    runtime_checkable,
)

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Model
from django.db.models.constants import LOOKUP_SEP
from django.utils.translation import gettext_lazy as _

import revy.abc
from revy.contrib.django import _typing
from revy.contrib.django.conf import settings
from revy.contrib.django.deletion import (
    CASCADE,
    SET,
    SET_DEFAULT,
    SET_NULL,
)
from revy.contrib.django.utils import (
    get_attribute_delta_model,
    get_delta_model,
    get_json_encoder_class,
    get_object_delta_model,
)


__all__ = (
    'CASCADE',
    'SET',
    'SET_DEFAULT',
    'SET_NULL',
    'AbstractRevision',
    'AbstractLazyRevision',
    'BaseRevision',
    'Revision',
    'AbstractDelta',
    'BaseDelta',
    'Delta',
    'AbstractObjectDelta',
    'BaseObjectDelta',
    'ObjectDelta',
    'AbstractAttributeDelta',
    'BaseAttributeDelta',
    'AttributeDelta',
    'ModelInstanceState',
    'get_model_instance_state',
)

from revy.dataclasses.metadata import (
    unwrap_metadata,
    wrap_metadata,
)


JSONEncoder = get_json_encoder_class()


class AbstractRevision(
    revy.abc.Revision,
    models.Model,
):

    DESCRIPTION_FIELD_NAME = 'description'

    CREATED_AT_FIELD_NAME = 'created_at'

    UPDATED_AT_FIELD_NAME = 'updated_at'

    class Meta:  # type: ignore[override]
        abstract = True

    def get_description(self) -> str:
        return getattr(self, self.__class__.DESCRIPTION_FIELD_NAME)

    def set_description(
        self,
        description: str,
    ) -> None:
        setattr(self, self.__class__.DESCRIPTION_FIELD_NAME, description)

    def get_deltas(self) -> _typing.QuerySet['AbstractDelta']:  # type: ignore[misc]
        delta_class = get_delta_model()
        deltas = delta_class.objects.filter(**{
            delta_class.REVISION_FIELD_NAME: self.pk,
        })
        return deltas

    def get_object_deltas(self) -> _typing.QuerySet['AbstractObjectDelta']:  # type: ignore[misc]
        delta_class = get_delta_model()
        object_delta_class = get_object_delta_model()
        q_lhs = LOOKUP_SEP.join([
            object_delta_class.PARENT_LINK_FIELD_NAME,
            delta_class.REVISION_FIELD_NAME,
        ])
        object_deltas = object_delta_class.objects.filter(**{
            q_lhs: self.pk,
        })
        return object_deltas

    def get_attribute_deltas(self) -> _typing.QuerySet['AbstractAttributeDelta']:  # type: ignore[misc]
        delta_class = get_delta_model()
        attribute_delta_class = get_attribute_delta_model()
        q_lhs = LOOKUP_SEP.join([
            attribute_delta_class.PARENT_LINK_FIELD_NAME,
            delta_class.REVISION_FIELD_NAME,
        ])
        attribute_deltas = attribute_delta_class.objects.filter(**{
            q_lhs: self.pk,
        })
        return attribute_deltas

    def get_actors(self) -> Iterable[Model]:
        seen: Set[Model] = set()
        for delta in self.get_deltas():
            actor = delta.get_actor()
            if actor is None:
                continue
            if actor in seen:
                continue
            yield actor
            seen.add(actor)

    def get_created_at(self) -> datetime.datetime:
        return getattr(self, self.__class__.CREATED_AT_FIELD_NAME)

    def set_created_at(
        self,
        created_at: datetime.datetime,
    ) -> None:
        setattr(self, self.__class__.CREATED_AT_FIELD_NAME, created_at)

    def get_updated_at(self) -> datetime.datetime:
        return getattr(self, self.__class__.UPDATED_AT_FIELD_NAME)

    def set_updated_at(
        self,
        updated_at: datetime.datetime,
    ) -> None:
        setattr(self, self.__class__.UPDATED_AT_FIELD_NAME, updated_at)


@runtime_checkable
class AbstractLazyRevision(
    revy.abc.LazyRevision,
    Protocol,
):

    def __call__(self) -> Optional[AbstractRevision]:
        ...


class BaseRevision(
    AbstractRevision,
    models.Model,
):

    description: _typing.TextField[
        str,
        str,
    ] = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=False,
        default='',
    )

    created_at: _typing.DateTimeField[
        datetime.datetime,
        datetime.datetime,
    ] = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
        blank=True,
        null=False,
        db_index=True,
    )

    updated_at: _typing.DateTimeField[
        datetime.datetime,
        datetime.datetime,
    ] = models.DateTimeField(
        verbose_name=_('updated at'),
        auto_now=True,
        blank=True,
        null=False,
        db_index=True,
    )

    class Meta:  # type: ignore[override]
        abstract = True


class Revision(
    BaseRevision,
    models.Model,
):

    class Meta:  # type: ignore[override]

        verbose_name = _('revision')

        verbose_name_plural = _('revisions')

        db_table = 'revy__revisions'

        swappable = settings.REVISION_MODEL_ATTNAME


class AbstractDelta(
    revy.abc.Delta,
    models.Model,
):

    PARENT_LINK_FIELD_NAME = 'delta_ptr'

    REVISION_FIELD_NAME = 'revision'

    ACTOR_FIELD_NAME = 'actor'

    ACTION_FIELD_NAME = 'action'

    ACTION_CREATE = 'Create'
    ACTION_UPDATE = 'Update'
    ACTION_DELETE = 'Delete'
    ACTION_SET = 'Set'
    ACTION_UNSET = 'Unset'

    ACTION_CHOICES = (
        (ACTION_CREATE, _('Create')),
        (ACTION_UPDATE, _('Update')),
        (ACTION_DELETE, _('Delete')),
        (ACTION_SET, _('Set')),
        (ACTION_UNSET, _('Unset')),
    )

    ACTION_MAX_LENGTH = max(map(lambda choice: len(choice[0]), ACTION_CHOICES))

    DESCRIPTION_FIELD_NAME = 'description'

    OBJECT_FIELD_NAME = 'content'

    CREATED_AT_FIELD_NAME = 'created_at'

    UPDATED_AT_FIELD_NAME = 'updated_at'

    class Meta:  # type: ignore[override]
        abstract = True

    def get_revision(self) -> AbstractRevision:
        return getattr(self, self.__class__.REVISION_FIELD_NAME)

    def set_revision(  # type: ignore[override]
        self,
        revision: AbstractRevision,
    ) -> None:
        setattr(self, self.__class__.REVISION_FIELD_NAME, revision)

    def get_actor(self) -> Optional[models.Model]:
        return getattr(self, self.__class__.ACTOR_FIELD_NAME)

    def set_actor(
        self,
        actor: Optional[models.Model],
    ) -> None:
        setattr(self, self.__class__.ACTOR_FIELD_NAME, actor)

    def get_action(self) -> str:
        return getattr(self, self.__class__.ACTION_FIELD_NAME)

    def set_action(
        self,
        action: str,
    ) -> None:
        setattr(self, self.__class__.ACTION_FIELD_NAME, action)

    def get_description(self) -> str:
        return getattr(self, self.__class__.DESCRIPTION_FIELD_NAME)

    def set_description(
        self,
        description: str,
    ) -> None:
        setattr(self, self.__class__.DESCRIPTION_FIELD_NAME, description)

    def get_object(self) -> Model:
        return getattr(self, self.__class__.OBJECT_FIELD_NAME)

    def set_object(
        self,
        object_: Model,
    ) -> None:
        setattr(self, self.__class__.OBJECT_FIELD_NAME, object_)

    def get_created_at(self) -> datetime.datetime:
        return getattr(self, self.__class__.CREATED_AT_FIELD_NAME)

    def set_created_at(
        self,
        created_at: datetime.datetime,
    ) -> None:
        setattr(self, self.__class__.CREATED_AT_FIELD_NAME, created_at)

    def get_updated_at(self) -> datetime.datetime:
        return getattr(self, self.__class__.UPDATED_AT_FIELD_NAME)

    def set_updated_at(
        self,
        updated_at: datetime.datetime,
    ) -> None:
        setattr(self, self.__class__.UPDATED_AT_FIELD_NAME, updated_at)


class BaseDelta(
    AbstractDelta,
    models.Model,
):

    revision: _typing.ForeignKey[
        AbstractRevision,
        AbstractRevision,
    ] = models.ForeignKey(
        verbose_name=_('revision'),
        to=settings.REVISION_MODEL,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        related_query_name='%(app_label)s_%(class)s',
        blank=False,
        null=False,
        db_column='revision_id',
    )

    actor_type: _typing.ForeignKey[
        Optional[ContentType],
        Optional[ContentType],
    ] = models.ForeignKey(
        verbose_name=_('actor type'),
        to=ContentType,
        on_delete=models.DO_NOTHING,
        related_name='%(app_label)s_%(class)s_set_created_by',
        related_query_name='%(app_label)s_%(class)s_created_by',
        blank=True,
        null=True,
        db_column='actor_type_id',
    )

    actor_id: _typing.TextField[
        Optional[str],
        Optional[str],
    ] = models.TextField(
        verbose_name=_('actor ID'),
        blank=True,
        null=True,
        default=None,
        db_index=True,
    )

    actor = GenericForeignKey(
        ct_field='actor_type',
        fk_field='actor_id',
    )

    action: _typing.CharField[
        str,
        str,
    ] = models.CharField(
        verbose_name=_('action'),
        max_length=AbstractDelta.ACTION_MAX_LENGTH,
        choices=AbstractDelta.ACTION_CHOICES,
        blank=False,
        null=False,
        db_index=True,
    )

    description: _typing.TextField[
        str,
        str,
    ] = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=False,
        default='',
    )

    content_type: _typing.ForeignKey[
        ContentType,
        ContentType,
    ] = models.ForeignKey(
        verbose_name=_('content type'),
        to=ContentType,
        on_delete=models.DO_NOTHING,
        related_name='%(app_label)s_%(class)s_set',
        related_query_name='%(app_label)s_%(class)s',
        blank=True,
        null=True,
        db_column='content_type_id',
    )

    content_id: _typing.TextField[
        Optional[str],
        Optional[str],
    ] = models.TextField(
        verbose_name=_('content ID'),
        blank=True,
        null=True,
        default=None,
        db_index=True,
    )

    content = GenericForeignKey(
        ct_field='content_type',
        fk_field='content_id',
    )

    created_at: _typing.DateTimeField[
        datetime.datetime,
        datetime.datetime,
    ] = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
        blank=True,
        null=False,
        db_index=True,
    )

    updated_at: _typing.DateTimeField[
        datetime.datetime,
        datetime.datetime,
    ] = models.DateTimeField(
        verbose_name=_('updated at'),
        auto_now=True,
        blank=True,
        null=False,
        db_index=True,
    )

    class Meta:  # type: ignore[override]
        abstract = True


class Delta(
    BaseDelta,
    models.Model,
):

    revision: _typing.ForeignKey[
        AbstractRevision,
        AbstractRevision,
    ] = models.ForeignKey(
        verbose_name=_('revision'),
        to=settings.REVISION_MODEL,
        on_delete=models.CASCADE,
        related_name='deltas',
        related_query_name='delta',
        blank=False,
        null=False,
        db_column='revision_id',
    )

    actor_type: _typing.ForeignKey[
        Optional[ContentType],
        Optional[ContentType],
    ] = models.ForeignKey(
        verbose_name=_('actor type'),
        to=ContentType,
        on_delete=models.DO_NOTHING,
        related_name='deltas_created_by',
        related_query_name='delta_created_by',
        blank=True,
        null=True,
        db_column='actor_type_id',
    )

    content_type: _typing.ForeignKey[
        ContentType,
        ContentType,
    ] = models.ForeignKey(
        verbose_name=_('content type'),
        to=ContentType,
        on_delete=models.DO_NOTHING,
        related_name='deltas',
        related_query_name='delta',
        blank=True,
        null=True,
        db_column='content_type_id',
    )

    class Meta:  # type: ignore[override]

        verbose_name = _('delta')

        verbose_name_plural = _('deltas')

        db_table = 'revy__deltas'

        swappable = settings.DELTA_MODEL_ATTNAME


class AbstractObjectDelta(
    revy.abc.ObjectDelta,
    AbstractDelta,
    models.Model,
):

    PARENT_LINK_FIELD_NAME = 'object_delta_ptr'

    class Meta:  # type: ignore[override]
        abstract = True

    def get_attribute_deltas(self) -> _typing.QuerySet['AbstractAttributeDelta']:  # type: ignore[misc]
        attribute_delta_class = get_attribute_delta_model()
        attribute_deltas = attribute_delta_class.objects.filter(**{
            attribute_delta_class.PARENT_LINK_FIELD_NAME: self.pk,
        })
        return attribute_deltas

    def get_actors(self) -> Iterable[Model]:
        seen: Set[Model] = set()
        actor = self.get_actor()
        if actor is not None:
            yield actor
            seen.add(actor)
        for attribute_delta in self.get_attribute_deltas():
            actor = attribute_delta.get_actor()
            if actor is None:
                continue
            if actor in seen:
                continue
            yield actor
            seen.add(actor)


class BaseObjectDelta(
    AbstractObjectDelta,
    models.Model,
):

    class Meta:  # type: ignore[override]
        abstract = True


class ObjectDelta(
    BaseObjectDelta,
    Delta,
):

    object_delta_ptr: _typing.OneToOneField[
        AbstractDelta,
        AbstractDelta,
    ] = models.OneToOneField(
        verbose_name=_('object delta pointer'),
        to=settings.DELTA_MODEL,
        on_delete=models.CASCADE,
        related_name='object_delta',
        related_query_name='object_delta',
        parent_link=True,
    )

    class Meta:  # type: ignore[override]

        verbose_name = _('object delta')

        verbose_name_plural = _('object deltas')

        db_table = 'revy__object_deltas'

        swappable = settings.OBJECT_DELTA_MODEL_ATTNAME


class AbstractAttributeDelta(
    revy.abc.AttributeDelta,
    AbstractDelta,
    models.Model,
):

    PARENT_LINK_FIELD_NAME = 'attribute_delta_ptr'

    OBJECT_DELTA_FIELD_NAME = 'parent'

    ATTRIBUTE_NAME_FIELD_NAME = 'field_name'

    OLD_VALUE_FIELD_NAME = 'old_value'

    NEW_VALUE_FIELD_NAME = 'new_value'

    class Meta:  # type: ignore[override]
        abstract = True

    def get_object_delta(self) -> AbstractObjectDelta:
        return getattr(self, self.__class__.OBJECT_DELTA_FIELD_NAME)

    def set_object_delta(  # type: ignore[override]
        self,
        object_delta: AbstractObjectDelta,
    ) -> None:
        setattr(self, self.__class__.OBJECT_DELTA_FIELD_NAME, object_delta)

    def get_attribute_name(self) -> str:
        return getattr(self, self.__class__.ATTRIBUTE_NAME_FIELD_NAME)

    def set_attribute_name(
        self,
        attribute_name: str,
    ) -> None:
        setattr(self, self.__class__.ATTRIBUTE_NAME_FIELD_NAME, attribute_name)

    def get_old_value(self) -> Optional[Any]:
        return getattr(self, self.__class__.OLD_VALUE_FIELD_NAME)

    def set_old_value(
        self,
        old_value: Optional[Any],
    ) -> None:
        setattr(self, self.__class__.OLD_VALUE_FIELD_NAME, old_value)

    def get_new_value(self) -> Optional[Any]:
        return getattr(self, self.__class__.NEW_VALUE_FIELD_NAME)

    def set_new_value(
        self,
        new_value: Optional[Any],
    ) -> None:
        setattr(self, self.__class__.NEW_VALUE_FIELD_NAME, new_value)


class BaseAttributeDelta(
    AbstractAttributeDelta,
    models.Model,
):

    parent: _typing.ForeignKey[
        AbstractObjectDelta,
        AbstractObjectDelta,
    ] = models.ForeignKey(
        verbose_name=_('object delta'),
        to=settings.OBJECT_DELTA_MODEL,
        on_delete=models.CASCADE,
        related_name='child_%(app_label)s_%(class)s_set',
        related_query_name='child_%(app_label)s_%(class)s',
        blank=False,
        null=False,
        db_column='parent_id',
    )

    field_name: _typing.TextField[
        str,
        str,
    ] = models.TextField(
        verbose_name=_('field name'),
        blank=False,
        null=False,
        db_index=True,
    )

    old_value = models.JSONField(
        verbose_name=_('old value'),
        encoder=JSONEncoder,
        blank=True,
        null=True,
        default=None,
    )

    new_value = models.JSONField(
        verbose_name=_('new value'),
        encoder=JSONEncoder,
        blank=True,
        null=True,
        default=None,
    )

    class Meta:  # type: ignore[override]
        abstract = True


class AttributeDelta(
    BaseAttributeDelta,
    Delta,
):

    attribute_delta_ptr: _typing.OneToOneField[
        AbstractDelta,
        AbstractDelta,
    ] = models.OneToOneField(
        verbose_name=_('attribute delta'),
        to=settings.DELTA_MODEL,
        on_delete=models.CASCADE,
        related_name='attribute_delta',
        related_query_name='attribute_delta',
        parent_link=True,
    )

    parent: _typing.ForeignKey[
        AbstractObjectDelta,
        AbstractObjectDelta,
    ] = models.ForeignKey(
        verbose_name=_('parent'),
        to=settings.OBJECT_DELTA_MODEL,
        on_delete=models.CASCADE,
        related_name='children',
        related_query_name='child',
        blank=False,
        null=False,
        db_column='parent_id',
    )

    class Meta:  # type: ignore[override]

        verbose_name = _('attribute delta')

        verbose_name_plural = _('attribute deltas')

        db_table = 'revy__attribute_deltas'

        swappable = settings.ATTRIBUTE_DELTA_MODEL_ATTNAME


@dataclasses.dataclass()
class ModelInstanceState:

    instance: Model = dataclasses.field()

    is_initialized: bool = dataclasses.field(
        kw_only=True,
        default=False,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    init_keys: List[str] = dataclasses.field(
        kw_only=True,
        default_factory=list,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    initial_values: Dict[str, Any] = dataclasses.field(
        kw_only=True,
        default_factory=dict,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    previous_values: Dict[str, Any] = dataclasses.field(
        kw_only=True,
        default_factory=dict,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    is_new: bool = dataclasses.field(
        kw_only=True,
        default=False,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    is_being_saved: bool = dataclasses.field(
        kw_only=True,
        default=False,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    is_saved: bool = dataclasses.field(
        kw_only=True,
        default=False,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    is_being_fetched: bool = dataclasses.field(
        kw_only=True,
        default=False,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    is_fetched: bool = dataclasses.field(
        kw_only=True,
        default=False,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    is_being_deleted: bool = dataclasses.field(
        kw_only=True,
        default=False,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    is_deleted: bool = dataclasses.field(
        kw_only=True,
        default=False,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    attribute_deltas: List[AbstractAttributeDelta] = dataclasses.field(
        kw_only=True,
        default_factory=list,
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    field_name_to_attribute_delta_index_mapping: DefaultDict[str, List[int]] = dataclasses.field(
        kw_only=True,
        default_factory=lambda: defaultdict(list),
        metadata=wrap_metadata(
            snapshot=True,
        ),
    )

    STATE_ATTNAME = '__revy__state'

    @classmethod
    def get_for(
        cls,
        instance: Model,
    ) -> Optional['ModelInstanceState']:
        return getattr(
            instance,
            cls.STATE_ATTNAME,
            None,
        )

    @classmethod
    def get_or_create_for(
        cls,
        instance: Model,
    ) -> 'ModelInstanceState':
        state = cls.get_for(instance)
        if state is not None:
            return state
        return cls(instance)

    def __post_init__(self) -> None:
        if self.__class__.get_for(self.instance) is None:
            setattr(self.instance, self.__class__.STATE_ATTNAME, self)

    def backup(self) -> Dict[str, Any]:
        snapshot = dict()
        for field in dataclasses.fields(self):
            metadata = unwrap_metadata(field)
            if metadata.get('snapshot', False):
                snapshot[field.name] = getattr(self, field.name)
                if isinstance(snapshot[field.name], (list, dict)):
                    snapshot[field.name] = snapshot[field.name].copy()
        return snapshot

    def restore(
        self,
        snapshot: Dict[str, Any],
    ) -> None:
        for field in dataclasses.fields(self):
            metadata = unwrap_metadata(field)
            if metadata.get('snapshot', False):
                setattr(self, field.name, snapshot.get(field.name))


def get_model_instance_state(
    instance: Model,
) -> ModelInstanceState:
    return ModelInstanceState.get_or_create_for(instance)
