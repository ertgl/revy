import unittest

import revy


class GlobalStorageTestCase(unittest.TestCase):

    def test_global_storage(self) -> None:
        self.assertIs(revy.Context._storage, revy.global_storage)
        self.assertIsInstance(revy.Context._storage, revy.Storage)
        self.assertIsInstance(revy.Context._storage, revy.ASGIRefLocalStorage)
