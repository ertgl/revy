import unittest

import revy


class ContextTestCase(unittest.TestCase):

    def test_simple_global_context_stack(self) -> None:
        with revy.Context():
            revy.Context.set_actor(1)

            with revy.Context():
                self.assertEqual(revy.Context.get_actor(), 1)
                revy.Context.set_actor(None)
                self.assertIsNone(revy.Context.get_actor())

            self.assertEqual(revy.Context.get_actor(), 1)
        self.assertIsNone(revy.Context.get_actor())

    def test_disable_enable(self) -> None:
        self.assertFalse(revy.Context.is_enabled())
        self.assertTrue(revy.Context.is_disabled())

        with revy.Context():
            self.assertFalse(revy.Context.is_disabled())
            self.assertTrue(revy.Context.is_enabled())

            with revy.Context():

                revy.Context.disable()

                self.assertFalse(revy.Context.is_enabled())
                self.assertTrue(revy.Context.is_disabled())

                with revy.Context():
                    self.assertFalse(revy.Context.is_enabled())
                    self.assertTrue(revy.Context.is_disabled())

                self.assertFalse(revy.Context.is_enabled())
                self.assertTrue(revy.Context.is_disabled())

            self.assertFalse(revy.Context.is_disabled())
            self.assertTrue(revy.Context.is_enabled())

        self.assertFalse(revy.Context.is_enabled())
        self.assertTrue(revy.Context.is_disabled())
