from django.test import TestCase
from revisions.models import (
    AttributeDelta,
    Delta,
    ObjectDelta,
    Revision,
)

from revy.contrib.django import (
    get_attribute_delta_model,
    get_delta_model,
    get_object_delta_model,
    get_revision_model,
)


class SwappableTestCase(TestCase):

    def test_swappable_models(self) -> None:
        self.assertIs(get_revision_model(), Revision)
        self.assertIs(get_delta_model(), Delta)
        self.assertIs(get_object_delta_model(), ObjectDelta)
        self.assertIs(get_attribute_delta_model(), AttributeDelta)
