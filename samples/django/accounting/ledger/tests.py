import decimal
from typing import (
    Callable,
    Optional,
    cast,
)

from django.contrib.auth import get_user_model
from django.db.models.options import Options
from django.test import TestCase
from ledger.models import (
    Account,
    Transaction,
)

import revy
import revy.abc
from revy.contrib.django.models import AbstractRevision
from revy.contrib.django.utils import (
    get_attribute_delta_model,
    get_delta_model,
    get_object_delta_model,
    get_revision_model,
)


User = get_user_model()

USER_MODEL_META = cast(Options, User._meta)  # noqa

USER_MODEL_FIELDS_COUNT = len(USER_MODEL_META.fields)

Revision = get_revision_model()

Delta = get_delta_model()

ObjectDelta = get_object_delta_model()

AttributeDelta = get_attribute_delta_model()

ACCOUNT_MODEL_META = cast(Options, Account._meta)  # noqa

ACCOUNT_MODEL_FIELDS_COUNT = len(ACCOUNT_MODEL_META.fields)

TRANSACTION_MODEL_META = cast(Options, Transaction._meta)  # noqa

TRANSACTION_MODEL_FIELDS_COUNT = len(TRANSACTION_MODEL_META.fields)


class LedgerTestCase(TestCase):

    def test_create_account(self) -> None:
        user = User.objects.create(username='tester')

        revision_counter = 0
        object_delta_counter = 0
        attribute_delta_counter = 0

        with revy.Context():
            revy.Context.set_actor(user)

            account = Account(code='E.0001')
            account.code = 'E.0002'
            account.code = 'E.0004'
            account.save()

            revision_counter += 1
            object_delta_counter += 1
            attribute_delta_counter += ACCOUNT_MODEL_FIELDS_COUNT

        self.assertEqual(Revision.objects.count(), revision_counter)
        self.assertEqual(ObjectDelta.objects.count(), object_delta_counter)
        self.assertEqual(AttributeDelta.objects.count(), attribute_delta_counter)

        revision = Revision.objects.latest('id')
        self.assertIn(user, revision.get_actors())

    def test_create_account_2(self) -> None:

        user = User.objects.create(username='tester')

        object_delta_counter = 0
        attribute_delta_counter = 0

        with revy.Context():
            revy.Context.set_actor(None)
            account = Account(code='E.0001')
            attribute_delta_counter += 1

            revy.Context.set_actor(user)

            account.code = 'E.0002'
            account.code = 'E.0004'
            account.save()

            object_delta_counter += 1
            attribute_delta_counter += ACCOUNT_MODEL_FIELDS_COUNT

        self.assertEqual(ObjectDelta.objects.count(), object_delta_counter)
        self.assertEqual(AttributeDelta.objects.count(), attribute_delta_counter)

    def test_create_transaction(self) -> None:

        user = User.objects.create(username='tester')

        revision_counter = 0
        object_delta_counter = 0
        attribute_delta_counter = 0

        with revy.Context():
            revy.Context.set_actor(user)
            account = Account(code='E.0001')
            account.save()

            revision_counter += 1
            object_delta_counter += 1
            attribute_delta_counter += ACCOUNT_MODEL_FIELDS_COUNT

            transaction = Transaction()
            transaction.account = account
            transaction.type = Transaction.TYPE_CREDIT
            transaction.amount = decimal.Decimal('1.00')
            transaction.iso_4217_code = 'TZS'
            transaction.exchange_rate = decimal.Decimal('2.00')
            transaction.save()

            revision_counter += 1
            object_delta_counter += 1
            attribute_delta_counter += TRANSACTION_MODEL_FIELDS_COUNT

        self.assertEqual(Revision.objects.count(), revision_counter)
        self.assertEqual(ObjectDelta.objects.count(), object_delta_counter)
        self.assertEqual(AttributeDelta.objects.count(), attribute_delta_counter)

    def test_update_transaction(self) -> None:

        user = User.objects.create(username='tester')
        account = Account.objects.create(code='E.0001')
        transaction = Transaction.objects.create(
            account=account,
            type=Transaction.TYPE_CREDIT,
            amount=decimal.Decimal('1.00'),
            iso_4217_code='TZS',
            exchange_rate=decimal.Decimal('2.00'),
        )

        revision_counter = 0
        object_delta_counter = 0
        attribute_delta_counter = 0

        with revy.Context():
            revy.Context.set_actor(user)
            transaction = Transaction.objects.get(pk=transaction.pk)

            transaction.amount = decimal.Decimal('2.00')
            attribute_delta_counter += 1

            transaction.save()
            revision_counter += 1
            attribute_delta_counter += 1
            object_delta_counter += 1

        self.assertEqual(Revision.objects.count(), revision_counter)
        self.assertEqual(ObjectDelta.objects.count(), object_delta_counter)
        self.assertEqual(AttributeDelta.objects.count(), attribute_delta_counter)

    def test_delete_account_cascading_transactions(self) -> None:

        user = User.objects.create(username='tester')

        account = Account.objects.create(code='E.0001')

        transactions_count = 10

        for _ in range(transactions_count):
            Transaction.objects.create(
                account=account,
                type=Transaction.TYPE_CREDIT,
                amount=decimal.Decimal('1.00'),
                iso_4217_code='TZS',
                exchange_rate=decimal.Decimal('2.00'),
            )

        revision_counter = 0
        object_delta_counter = 0
        attribute_delta_counter = 0

        with revy.Context():
            revy.Context.set_actor(user)
            account = Account.objects.get(pk=account.pk)
            account.delete()
            revision_counter += 1
            revision_counter += transactions_count
            object_delta_counter += 1
            object_delta_counter += transactions_count

        self.assertEqual(Revision.objects.count(), revision_counter)
        self.assertEqual(ObjectDelta.objects.count(), object_delta_counter)
        self.assertEqual(AttributeDelta.objects.count(), attribute_delta_counter)

    def test_group_deltas_by_revision(self) -> None:

        def get_lazy_revision() -> Callable[[], AbstractRevision]:

            revision: Optional[AbstractRevision] = None

            def get_or_create_revision() -> AbstractRevision:
                nonlocal revision
                if revision is None:
                    revision = Revision()
                    revision.set_description(revy.Context.get_revision_description())
                    revision.save()
                return revision

            return get_or_create_revision

        object_delta_counter = 0

        with revy.Context.via_revision(get_lazy_revision()):

            account = Account.objects.create(code='E.0001')
            object_delta_counter += 1

            transactions_count = 10

            for _ in range(transactions_count):
                Transaction.objects.create(
                    account=account,
                    type=Transaction.TYPE_CREDIT,
                    amount=decimal.Decimal('1.00'),
                    iso_4217_code='TZS',
                    exchange_rate=decimal.Decimal('2.00'),
                )
            object_delta_counter += transactions_count

            lazy_revision = revy.Context.get_revision()
            if callable(lazy_revision):
                lazy_revision = lazy_revision()

            self.assertEqual(Revision.objects.count(), 1)
            self.assertEqual(ObjectDelta.objects.filter(revision=lazy_revision).count(), object_delta_counter)
