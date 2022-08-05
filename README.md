### [Revy](#)

A toolkit for building revision control systems.

---

:warning: Currently only [Django](https://www.djangoproject.com/) support is available.

---


## Features

With this library, you can produce various revision control systems for your data.
When Revy is used without any customization, it simply gives you a revision history.

All the models in the package are swappable. So, you are free to expand the logic
by writing your own models instead of using the default ones.

### Idiomatic and Declarative Syntax

Write the code as you think. When you enter a Revy context, it tracks all the changes
automatically.

```python
from revy import Context


with (
  Context.via_actor(None),
  Context.via_revision_description("Detected by the system."),
):
    comment.is_marked_as_spam = True
    comment.save()
```


Context management is done by the [Stackholm](https://github.com/ertgl/stackholm/) project.
The implementation is both space and time efficient, also sync / async compatible.
Context (or stack) operations have O(1) time complexity, and they are zero-copy.
(Except the methods prefixed by `via_`. They are O(n) in the worst case, where n is the
number of checkpoint datas to be set, which constantly equals to 1. That makes them amortized O(1).)


### Generic Actors

Actors can be any instance of any model.

```python
@Context()
def view(request):
    if request.META.get('HTTP_X_PERFORM_AS_ORGANIZATION'):
        Context.set_actor(request.organization)
    else:
        Context.set_actor(request.user)
```


### Multiple Actors In One Revision

Revy can be used in collaborative systems too. Multiple actors can be
involved together in one revision.

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
                C.via_actor(None),
                C.via_attribute_delta_description(
                    'Corrected by the system.',
                ),
            ):
                # <-- The actor is `None` in this block.
                instance.local_amount = local_amount
            # <-- The actor here is `request.user` again.
        instance.save()
```


### Disabling Automatic Delta Generation Temporarily

When you need it, you can write code like below to disable / re-enable the tracking.

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


### Foreign Key Deletion Handler

Revy has drop in replacements for Django's foreign key deletion handlers.

If there is no active context or the existing context is disabled during
the deletion, fallbacks to the corresponding Django deletion handler.

**Supported handler types:**

- `CASCADE`
- `SET`
- `SET_NULL`
- `SET_DEFAULT`

```python
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


### Getting Snapshots of Object Deltas

Revy provides an ORM function called as `ObjectSnapshot`. It helps
to reconstruct model instances from deltas which are relative to 
the object deltas, using only one query.

For instance, the following example can be considered as a rollback operation.

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


## Installation

Revy is available on [PyPI](https://pypi.org/project/revy/).
It can be installed and upgraded using [pip](https://pip.pypa.io):

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

___

## License

See the [LICENSE](https://github.com/ertgl/revy/blob/main/LICENSE) file.
