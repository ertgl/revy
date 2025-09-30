### Revy

A toolkit for building revision control systems around
[Django](https://www.djangoproject.com/) models.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
  - [Polymorphic Actor Types](#polymorphic-actor-types)
  - [Collaborative Revisions](#collaborative-revisions)
  - [Foreign Key Deletion Handlers](#foreign-key-deletion-handlers)
  - [Snapshots and Rollbacks](#snapshots-and-rollbacks)
  - [Disabling Tracking Temporarily](#disabling-tracking-temporarily)
- [Glossary](#glossary)
- [License](#license)

## Overview

Revy is a powerful toolkit for building revision control systems for Django
models. It provides a flexible framework to automatically track changes to
model instances, enabling the creation of detailed revision histories. Whether
you need to track simple modifications or manage complex collaborative
revisions, Revy delivers a very fast, efficient, and easy-to-use solution.

Revy monitors changes at both the object and attribute levels, storing them in
a **tabular format** for straightforward querying and analysis. It supports
**polymorphic actor types**, allowing actors to be instances of any model, and
enables customization of database models through Django's **swappable models**
feature. Revy also provides drop-in replacements for Django's
**foreign key deletion handlers**, simplifying the tracking of cascading
deletions and related changes. For snapshots and rollbacks, Revy offers the
`ObjectSnapshot` ORM function, which reconstructs model instances from object
deltas using a single query.

The tracking system is organized around contexts, which provide a managed scope
for revisions, actors, and changes. Contexts can be temporarily disabled or
re-enabled as needed, giving developers full control over when and how changes
are tracked.

Under the hood, Revy patches Django models to add tracking functionality and
leverages the [stackholm](https://github.com/ertgl/stackholm/) project to
manage contexts as indexed stacks. This enables zero-copy context operations
with O(1) time complexity (amortized), making the solution highly efficient in
both time and memory.

Revy's implementation is compatible with both synchronous and asynchronous
workflows, ensuring smooth integration into both new and existing Django
projects.

## Installation

Revy is available on PyPI. It can be installed using any compatible package
manager, such as `pip`:

```shell
pip install revy
```

## Setup

Add `'revy.contrib.django'` to `INSTALLED_APPS` in your Django project.


```python
INSTALLED_APPS = [
  'revy.contrib.django',
]
```

## Usage

Simply wrap your code in a context block to enable automatic tracking.

```python
from revy import Context


with (
  Context.via_actor(None),
  Context.via_revision_description("Detected by the system."),
):
    # Changes made in this block will be tracked automatically.
    comment.is_marked_as_spam = True
    # Saving the instance will create a new revision.
    comment.save()
```

### Polymorphic Actor Types

Revy uses polymorphic relationships to associate actors with revisions. This
means that actors can be instances of any model, e.g., user, organization,
system, etc.

```python
@Context()
def view(request):
    # If the request was made on behalf of an organization,
    # set the actor as the organization.
    if (
      # Check if the request has an HTTP header to perform as an organization.
      request.META.get('HTTP_X_PERFORM_AS_ORGANIZATION')
      and request.organization is not None
    ):
        Context.set_actor(request.organization)
    else:
        Context.set_actor(request.user)
```

### Collaborative Revisions

Revy supports collaborative systems, allowing multiple actors in a single
revision.

```python
from revy import Context as C


def deserialize(data):
    ...


def view(request):
    with C.via_actor(request.user):
        # <-- The actor is `request.user` in this block.
        C.set_revision_description(
            request.META.get('HTTP_X_COMMIT_MESSAGE'),
        )
        instance = deserialize(request.data)
        local_amount = instance.amount * instance.exchange_rate
        if instance.local_amount != local_amount:
            with (
                # Assume that `None` is the system.
                C.via_actor(None),
                C.via_attribute_delta_description(
                    'Corrected by the system.',
                ),
            ):
                # <-- The actor is the system in this block.
                instance.local_amount = local_amount
            # <-- The actor here is `request.user` again.
        instance.save()
```

### Foreign Key Deletion Handlers

Revy provides drop-in replacements for Django's foreign key deletion handlers.

If no active context exists or if the current context is disabled during
deletion, the corresponding Django handler will be used as a fallback.

**Supported handler types:**

- `CASCADE`
- `SET`
- `SET_DEFAULT`
- `SET_NULL`

```python
# Import `CASCADE` from `revy.contrib.django.models` module
# instead of `django.db.models` module, to use revy's handler.
from revy.contrib.django.models import CASCADE

class Post(Model):
    author = ForeignKey(
        User,
        on_delete=CASCADE,
    )
```

```python
with (
    Context.via_object_delta_description(
        "The account has been closed at the owner's request.",
    ),
    Context.via_deletion_description(
        "Deleted because the owner's account has been closed.",
    ),
):
    user.delete()
```

### Snapshots and Rollbacks

Revy provides an ORM function named as `ObjectSnapshot` to reconstruct
model instances from object deltas with a single query.

The following example demonstrates a rollback operation:

```python
from django.contrib.contenttypes.models import ContentType
from revy.contrib.django.models import (
    ObjectDelta,
    ObjectSnapshot,
)


DELETED_USER_ID = 1


object_delta = ObjectDelta.objects.filter(
    action=ObjectDelta.ACTION_DELETE,
    content_type=ContentType.objects.get_for_model(User),
    content_id=DELETED_USER_ID,
).annotate(
    snapshot=ObjectSnapshot(User)
).order_by(
    '-pk',
).first()

# object_delta.snapshot is an instance of User class.
# And it is ready to be saved again, with the same ID if you don't change it.
object_delta.snapshot.save()
```

### Disabling Tracking Temporarily

Tracking can be disabled and re-enabled as needed.

```python
@Context()
def some_task():
    Context.disable()
    ...
    Context.enable()
```

```python
@Context()
def some_task():
    with Context.as_disabled():
        ... # <-- Context is disabled in this block.
    # <-- Here context is re-enabled.
```

## Glossary

- **Actor**: An entity (e.g., user, organization, system, etc.) responsible for
  making changes.
- **Attribute delta**: A change made to a model instance's attribute (e.g., set,
  unset).
- **Context**: A managed scope that tracks revisions, actors, and changes.
- **Delta**: Either an object delta or an attribute delta.
- **Object delta**: A change made to a model instance (e.g., create, update,
  delete). An object delta can contain multiple attribute deltas.
- **Revision**: A collection of deltas made by one or more actors.
- **Snapshot**: A record of an object's state at a specific point in time
  (e.g., before a change).

## License

This project is licensed under the
[MIT License](https://opensource.org/license/mit).

See the [LICENSE](LICENSE) file for more details.
