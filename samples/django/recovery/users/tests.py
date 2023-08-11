from typing import cast

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from users.models import (
    Group,
    User,
    UserGroupRelationship,
)

from revy import Context
from revy.contrib.django.aggregates import ObjectSnapshot
from revy.contrib.django.models import ObjectDelta


class UsersTestCase(TestCase):
    @Context()
    def test_reconstructing_removed_user_group_relationship(self) -> None:
        user = User.objects.create(username="ertgl")
        group = Group.objects.create(name="Users")
        user_group_relationship = UserGroupRelationship.objects.create(
            user=user,
            group=group,
        )

        self.assertEqual(user.groups.count(), 1)

        removed_user_group_relationship_pk = user_group_relationship.pk
        user_group_relationship.delete()

        self.assertEqual(user.groups.count(), 0)

        user_group_relationship_content_type = ContentType.objects.get_for_model(  # type: ignore[attr-defined]
            UserGroupRelationship,
        )

        object_delta = (
            ObjectDelta.objects.filter(
                action=ObjectDelta.ACTION_DELETE,
                content_type=user_group_relationship_content_type,
                content_id=removed_user_group_relationship_pk,
            )
            .annotate(recovered_snapshot=ObjectSnapshot(UserGroupRelationship))
            .order_by(
                "-pk",
            )
            .first()
        )

        self.assertIsNotNone(object_delta)

        recovered_user_group_relationship = getattr(
            object_delta, "recovered_snapshot", None
        )
        self.assertIsNotNone(recovered_user_group_relationship)
        self.assertEqual(user.groups.count(), 0)

        recovered_user_group_relationship = cast(
            UserGroupRelationship, recovered_user_group_relationship
        )
        recovered_user_group_relationship.save()
        self.assertEqual(user.groups.count(), 1)

        self.assertEqual(
            recovered_user_group_relationship.pk, removed_user_group_relationship_pk
        )
        self.assertEqual(recovered_user_group_relationship.user, user)
        self.assertEqual(recovered_user_group_relationship.group, group)
