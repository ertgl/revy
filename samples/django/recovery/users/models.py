from django.db.models import (
    CharField,
    ForeignKey,
    ManyToManyField,
    Model,
)

from revy.contrib.django.deletion import CASCADE


class User(Model):

    username = CharField(  # type: ignore
        max_length=40,
        unique=True,
    )

    groups = ManyToManyField(  # type: ignore
        'users.Group',
        through='users.UserGroupRelationship',
        through_fields=('user', 'group'),
        related_name='users',
        related_query_name='user',
    )


class Group(Model):

    name = CharField(  # type: ignore
        max_length=255,
        unique=True,
    )


class UserGroupRelationship(Model):

    user = ForeignKey(  # type: ignore
        User,
        on_delete=CASCADE,
        related_name='group_relationships',
        related_query_name='group_relationship',
        blank=False,
        null=False,
    )

    group = ForeignKey(  # type: ignore
        Group,
        on_delete=CASCADE,
        related_name='user_relationships',
        related_query_name='user_relationship',
        blank=False,
        null=False,
    )

    class Meta:

        unique_together = [
            ('user', 'group'),
        ]
