import unittest

import revy


class ASGIRefLocalStorageTestCase(unittest.TestCase):

    def test_get_base_context_class(self) -> None:
        self.assertIs(revy.ASGIRefLocalStorage.get_base_context_class(), revy.Context)

    def test_create_context_class(self) -> None:
        storage = revy.ASGIRefLocalStorage()
        context_class = storage.create_context_class()
        self.assertTrue(issubclass(context_class, revy.Context))
