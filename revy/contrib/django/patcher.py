from contextlib import (
    ExitStack,
    suppress,
)
import dataclasses
import functools
import inspect
from typing import (
    Any,
    Callable,
    Optional,
    TYPE_CHECKING,
    Type,
    cast,
)

from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.models import (
    Field,
    Model,
)
from django.db.models.options import Options

from revy.context import Context
from revy.contrib.django.utils import (
    get_attribute_delta_model,
    get_delta_model,
    get_object_delta_model,
    get_revision_model,
)


if TYPE_CHECKING:
    from revy.contrib.django.models import AbstractRevision  # noqa


__all__ = (
    'Patcher',
    'MethodPatchData',
)


@dataclasses.dataclass()
class MethodPatchData:

    type_: type = dataclasses.field(
        kw_only=True,
    )

    method_name: str = dataclasses.field(
        kw_only=True,
    )

    original_method: Callable[..., Any] = dataclasses.field(
        kw_only=True,
    )

    patched_method: Callable[..., Any] = dataclasses.field(
        kw_only=True,
    )


class Patcher:

    PATCH_DATA_ATTNAME = '__revy__patch_data'

    @classmethod
    def get_method_patch_data(
        cls,
        type_: type,
        method_name: str,
    ) -> Optional[MethodPatchData]:
        attribute = getattr(type_, method_name, None)
        patch_data = getattr(attribute, cls.PATCH_DATA_ATTNAME, None)
        if isinstance(patch_data, MethodPatchData):
            return patch_data
        return None

    @classmethod
    def is_method_patched(
        cls,
        type_: type,
        method_name: str,
    ) -> bool:
        return cls.get_method_patch_data(type_, method_name) is not None

    @classmethod
    def apply_method_patch(
        cls,
        method_patch_data: MethodPatchData,
    ) -> None:
        setattr(
            method_patch_data.type_,
            method_patch_data.method_name,
            method_patch_data.patched_method,
        )
        setattr(
            method_patch_data.patched_method,
            cls.PATCH_DATA_ATTNAME,
            method_patch_data,
        )

    @classmethod
    def unpatch_method(
        cls,
        type_: type,
        method_name: str,
    ) -> None:
        method_patch_data = cls.get_method_patch_data(type_, method_name)
        if method_patch_data is None:
            return
        setattr(
            method_patch_data.type_,
            method_patch_data.method_name,
            method_patch_data.original_method,
        )
        delattr(
            method_patch_data.patched_method,
            cls.PATCH_DATA_ATTNAME,
        )

    @classmethod
    def patch_model(
        cls,
        model: Type[Model],
    ) -> None:
        excluded_models = (
            get_revision_model(),
            get_delta_model(),
            get_object_delta_model(),
            get_attribute_delta_model(),
        )
        if issubclass(model, excluded_models):
            return
        cls.patch_model_init(model)
        cls.patch_model_setattr(model)
        cls.patch_model_save_base(model)
        cls.patch_model_refresh_from_db(model)
        cls.patch_model_delete(model)

    @classmethod
    def unpatch_model(
        cls,
        model: Type[Model],
    ) -> None:
        cls.unpatch_model_init(model)
        cls.unpatch_model_setattr(model)
        cls.unpatch_model_save_base(model)
        cls.unpatch_model_refresh_from_db(model)
        cls.unpatch_model_delete(model)

    @classmethod
    def patch_model_init(
        cls,
        model: Type[Model],
    ) -> None:

        if cls.is_method_patched(model, '__init__'):
            return

        from revy.contrib.django.models import get_model_instance_state

        original_init = cast(
            Callable[..., None],
            model.__init__,
        )

        @functools.wraps(original_init)
        def patched_init(
            self: Model,
            *args: Any,
            **kwargs: Any,
        ) -> None:

            if Context.is_disabled():
                return original_init(self, *args, **kwargs)

            current_frame = inspect.currentframe()
            previous_frame = current_frame.f_back if current_frame else None
            caller_name = previous_frame.f_code.co_name if previous_frame else None
            caller_locals = previous_frame.f_locals if previous_frame else dict()
            caller_class = caller_locals.get('cls', self.__class__)
            caller_class_is_model = inspect.isclass(caller_class) and issubclass(caller_class, Model)
            caller_class_method_is_from_db = caller_class_is_model and caller_name == 'from_db'

            state = get_model_instance_state(self)

            state.init_keys = list(kwargs.keys())

            state.is_initialized = False

            state.is_new = not caller_class_method_is_from_db

            state.is_being_saved = False
            state.is_saved = False

            state.is_being_fetched = caller_class_method_is_from_db
            state.is_fetched = False

            state.is_being_deleted = False
            state.is_deleted = False

            original_init(self, *args, **kwargs)

            state.is_initialized = True

            state.is_being_fetched = False
            state.is_fetched = not state.is_new

        method_patch_data = MethodPatchData(
            type_=model,
            method_name='__init__',
            original_method=original_init,
            patched_method=patched_init,
        )

        cls.apply_method_patch(method_patch_data)

    @classmethod
    def unpatch_model_init(
        cls,
        model: Type[Model],
    ) -> None:
        cls.unpatch_method(model, '__init__')

    @classmethod
    def patch_model_setattr(
        cls,
        model: Type[Model],
    ) -> None:

        if cls.is_method_patched(model, '__setattr__'):
            return

        from revy.contrib.django.models import get_model_instance_state

        original_setattr = cast(
            Callable[..., None],
            model.__setattr__,
        )

        @functools.wraps(original_setattr)
        def patched_setattr(
            self: Model,
            attname: str,
            value: Any,
        ) -> None:

            if Context.is_disabled():
                return original_setattr(self, attname, value)

            meta = cast(Options, model._meta)  # noqa

            field: Optional[Field] = None
            with suppress(FieldDoesNotExist):
                field = cast(Field, meta.get_field(attname))
            if field is None:
                return original_setattr(self, attname, value)
            if field.one_to_many or field.many_to_many:
                return original_setattr(self, attname, value)

            new_value = value
            if field.is_relation and isinstance(value, Model):
                related_model = cast(Type[Model], value.__class__)
                related_meta = cast(Options, related_model._meta)  # noqa
                related_pk = related_meta.pk
                if related_pk is None:
                    return original_setattr(self, attname, value)
                new_value = value.__dict__.get(related_pk.attname)

            state = get_model_instance_state(self)

            is_initial = field.attname in state.init_keys or field.name in state.init_keys
            is_caused_by_system = not state.is_initialized and not is_initial
            is_caused_by_system |= state.is_being_saved
            is_caused_by_system |= state.is_being_fetched
            is_caused_by_system |= state.is_being_deleted

            old_value = state.previous_values.get(field.attname)
            is_changed = old_value != new_value
            if is_changed:
                state.previous_values[field.attname] = new_value

            original_setattr(self, attname, value)

            if state.is_being_fetched:
                return

            if not is_changed:
                return

            attribute_delta_class = get_attribute_delta_model()

            with Context():

                if is_caused_by_system:
                    Context.set_actor(None)

                previous_attribute_delta_indexes = state.field_name_to_attribute_delta_index_mapping.get(
                    field.attname,
                    [],
                )

                previous_attribute_delta_index: Optional[int] = None
                with suppress(IndexError):
                    previous_attribute_delta_index = previous_attribute_delta_indexes[-1]

                previous_attribute_delta = (
                    state.attribute_deltas[previous_attribute_delta_index]
                    if previous_attribute_delta_index is not None
                    else None
                )

                previous_actor = (
                    previous_attribute_delta.get_actor()
                    if previous_attribute_delta is not None
                    else None
                )

                actor = Context.get_actor()

                is_first_delta = state.is_new and len(previous_attribute_delta_indexes) == 0

                action = (
                    attribute_delta_class.ACTION_SET
                    if is_first_delta or new_value not in (None, False, '')
                    else attribute_delta_class.ACTION_UNSET
                )

                description = Context.get_attribute_delta_description()

                was_default = state.is_new
                was_default &= previous_actor is None
                was_default &= (
                    field.default in [previous_attribute_delta.get_new_value(), None]
                    if previous_attribute_delta is not None
                    else False
                )

                was_caused_by_system = state.is_initialized and previous_actor is None
                was_caused_by_system &= not is_initial

                should_discard_new_attribute_delta = previous_attribute_delta is not None
                should_discard_new_attribute_delta &= (previous_actor is actor) or was_caused_by_system
                should_discard_new_attribute_delta |= was_default

                concrete_attribute_delta = (
                    previous_attribute_delta
                    if should_discard_new_attribute_delta
                    else attribute_delta_class()
                )

                assert concrete_attribute_delta is not None  # noqa

                concrete_attribute_delta.set_action(action)
                concrete_attribute_delta.set_description(description)
                concrete_attribute_delta.set_new_value(new_value)

                if not should_discard_new_attribute_delta:

                    concrete_attribute_delta.set_actor(actor)
                    concrete_attribute_delta.set_attribute_name(field.attname)
                    concrete_attribute_delta.set_old_value(old_value)

                    state.attribute_deltas.append(concrete_attribute_delta)
                    attribute_delta_index = len(state.attribute_deltas) - 1
                    state.field_name_to_attribute_delta_index_mapping[field.attname].append(
                        attribute_delta_index,
                    )

        method_patch_data = MethodPatchData(
            type_=model,
            method_name='__setattr__',
            original_method=original_setattr,
            patched_method=patched_setattr,
        )

        cls.apply_method_patch(method_patch_data)

    @classmethod
    def unpatch_model_setattr(
        cls,
        model: Type[Model],
    ) -> None:
        cls.unpatch_method(model, '__setattr__')

    @classmethod
    def patch_model_save_base(
        cls,
        model: Type[Model],
    ) -> None:

        if cls.is_method_patched(model, 'save_base'):
            return

        from revy.contrib.django.models import get_model_instance_state

        original_save_base = cast(
            Callable[..., None],
            model.save_base,
        )

        @functools.wraps(original_save_base)
        def patched_save_base(
            self: Model,
            *args: Any,
            **kwargs: Any,
        ) -> None:

            if Context.is_disabled():
                return original_save_base(self, *args, **kwargs)

            state = get_model_instance_state(self)

            snapshot = state.backup()

            def restore_state() -> None:
                state.restore(snapshot)

            was_new = state.is_new
            state.is_being_saved = True

            with ExitStack() as exit_stack, transaction.atomic():

                exit_stack.callback(restore_state)
                original_save_base(self, *args, **kwargs)
                exit_stack.pop_all()

                revision = Context.get_revision()
                if revision is None:
                    revision_class = get_revision_model()
                    revision = revision_class()
                    revision.set_description(Context.get_revision_description())
                    revision.save()
                revision = cast('AbstractRevision', revision)

                object_delta_class = get_object_delta_model()

                action = (
                    object_delta_class.ACTION_CREATE
                    if was_new
                    else object_delta_class.ACTION_UPDATE
                )

                object_delta = object_delta_class()
                object_delta.set_revision(revision)
                object_delta.set_actor(Context.get_actor())
                object_delta.set_action(action)
                object_delta.set_description(Context.get_object_delta_description())
                object_delta.set_object(self)
                object_delta.save()

                for attribute_delta in state.attribute_deltas:
                    attribute_delta.set_revision(revision)
                    attribute_delta.set_object_delta(object_delta)
                    attribute_delta.set_object(self)
                    attribute_delta.save()
                state.attribute_deltas.clear()
                state.field_name_to_attribute_delta_index_mapping.clear()

                state.is_new = False

                state.is_being_saved = False
                state.is_saved = True

                state.is_being_fetched = False
                state.is_fetched = False

                state.is_being_deleted = False
                state.is_deleted = False

        method_patch_data = MethodPatchData(
            type_=model,
            method_name='save_base',
            original_method=original_save_base,
            patched_method=patched_save_base,
        )

        cls.apply_method_patch(method_patch_data)

    @classmethod
    def unpatch_model_save_base(
        cls,
        model: Type[Model],
    ) -> None:
        cls.unpatch_method(model, 'save_base')

    @classmethod
    def patch_model_refresh_from_db(
        cls,
        model: Type[Model],
    ) -> None:

        if cls.is_method_patched(model, 'refresh_from_db'):
            return

        from revy.contrib.django.models import get_model_instance_state

        original_refresh_from_db = cast(
            Callable[..., None],
            model.refresh_from_db,
        )

        @functools.wraps(original_refresh_from_db)
        def patched_refresh_from_db(
            self: Model,
            *args: Any,
            **kwargs: Any,
        ) -> None:

            if Context.is_disabled():
                return original_refresh_from_db(self, *args, **kwargs)

            state = get_model_instance_state(self)

            snapshot = state.backup()

            def restore_state() -> None:
                state.restore(snapshot)

            state.is_being_fetched = True

            with ExitStack() as exit_stack:
                exit_stack.callback(restore_state)
                original_refresh_from_db(self, *args, **kwargs)
                exit_stack.pop_all()

                for attribute_delta in state.attribute_deltas:
                    attribute_delta.set_object(self)

                state.is_new = False

                state.is_being_saved = False
                state.is_saved = False

                state.is_being_fetched = False
                state.is_fetched = True

                state.is_being_deleted = False
                state.is_deleted = False

        method_patch_data = MethodPatchData(
            type_=model,
            method_name='refresh_from_db',
            original_method=original_refresh_from_db,
            patched_method=patched_refresh_from_db,
        )

        cls.apply_method_patch(method_patch_data)

    @classmethod
    def unpatch_model_refresh_from_db(
        cls,
        model: Type[Model],
    ) -> None:
        cls.unpatch_method(model, 'refresh_from_db')

    @classmethod
    def patch_model_delete(
        cls,
        model: Type[Model],
    ) -> None:

        if cls.is_method_patched(model, 'delete'):
            return

        from revy.contrib.django.models import get_model_instance_state

        original_delete = cast(
            Callable[..., None],
            model.delete,
        )

        @functools.wraps(original_delete)
        def patched_delete(
            self: Model,
            *args: Any,
            **kwargs: Any,
        ) -> None:

            if Context.is_disabled():
                return original_delete(self, *args, **kwargs)

            state = get_model_instance_state(self)

            snapshot = state.backup()

            def restore_state() -> None:
                state.restore(snapshot)

            state.is_being_deleted = True

            with ExitStack() as exit_stack, transaction.atomic():

                exit_stack.callback(restore_state)

                revision = Context.get_revision()
                if revision is None:
                    revision_class = get_revision_model()
                    revision = revision_class()
                    revision.set_description(Context.get_revision_description())
                    revision.save()
                revision = cast('AbstractRevision', revision)

                object_delta_class = get_object_delta_model()
                object_delta = object_delta_class()
                object_delta.set_revision(revision)
                object_delta.set_actor(Context.get_actor())
                object_delta.set_action(object_delta_class.ACTION_DELETE)
                object_delta.set_description(Context.get_object_delta_description())
                object_delta.set_object(self)
                object_delta.save()

                for attribute_delta in state.attribute_deltas:
                    attribute_delta.set_revision(revision)
                    attribute_delta.set_object(self)
                    attribute_delta.save()
                state.attribute_deltas.clear()
                state.field_name_to_attribute_delta_index_mapping.clear()

                original_delete(self, *args, **kwargs)
                exit_stack.pop_all()

                state.is_new = False

                state.is_being_saved = False
                state.is_saved = False

                state.is_being_fetched = False
                state.is_fetched = False

                state.is_being_deleted = False
                state.is_deleted = True

        method_patch_data = MethodPatchData(
            type_=model,
            method_name='delete',
            original_method=original_delete,
            patched_method=patched_delete,
        )

        cls.apply_method_patch(method_patch_data)

    @classmethod
    def unpatch_model_delete(
        cls,
        model: Type[Model],
    ) -> None:
        cls.unpatch_method(model, 'delete')
