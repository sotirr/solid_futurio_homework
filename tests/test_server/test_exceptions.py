"""Tests for custom excemtions."""

from unittest import TestCase

from SpaceBattle.server.exceptions import Error, NotMovableError, NotRotableError


class BaseErrorTests(TestCase):
    """Tests for base error class."""

    def test_raises(self):
        """Test that raises."""
        with self.assertRaises(Error):
            raise Error


class NotMovableErrorTests(TestCase):
    """Tests for NotMovableError class."""

    def test_default_message(self):
        """Test exception default message."""
        err = NotMovableError()
        self.assertEqual(err.message, 'The object cannot be moved.')


class NotRotableErrorTests(TestCase):
    """Tests for NotRotableError class."""

    def test_default_message(self):
        """Test exception default message."""
        err = NotRotableError()
        self.assertEqual(err.message, 'The object cannot be rotated.')
