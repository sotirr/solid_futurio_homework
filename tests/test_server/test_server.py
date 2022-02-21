"""Tests for server module."""
from unittest import TestCase
from unittest.mock import patch

import numpy as np
from SpaceBattle.server.exceptions import NotMovableError, NotRotableError

from SpaceBattle.server.commands import MoveCommand, RotateCommand


class FakeMovableClass:
    """Fake movable class."""

    def __init__(self, position: np.ndarray, move_velocity: np.ndarray) -> None:
        """
        Init variabels.

        position - object's position on the map
        move_velocity - movement instantaneous speed
        """
        self._move_velocity: np.ndarray = move_velocity
        self._position: np.ndarray = position
        super().__init__()

    def get_position(self) -> np.ndarray:
        """Get current object's position on the map."""
        return self._position

    def set_position(self, position: np.ndarray) -> None:
        """Set new object's position."""
        self._position = position

    def get_movement_velocity(self) -> np.ndarray:
        """Get object's movement velocity."""
        return self._move_velocity


class FakeRotableClass:
    """Fake rotable class."""

    def __init__(self, direction: int, rotate_velocity: int) -> None:
        """
        Init variabels.

        direction - corrent object's direction in degrees
        rotate_velocity - object's rotate velocity in degrees
        """
        self._direction = direction
        self._rotate_velocity = rotate_velocity
        super().__init__()

    def get_direction(self) -> int:
        """Retrun object's current direction in degrees range from -360 to +360."""
        return self._direction

    def get_rotation_velocity(self) -> int:
        """Retrun object rotation velocity in degrees range from -360 to +360."""
        return self._rotate_velocity

    def set_direction(self, direction: int) -> None:
        """Set a new object's direction."""
        self._direction = direction


class TestMoveCommand(TestCase):
    """Tests for the move command."""

    def test_move(self):
        """
        Test move.

        Для объекта, находящегося в точке (12, 5) и движущегося со скоростью (-7, 3)
        движение меняет положение объекта на (5, 8).
        """
        test_fail_msg: str = """
        The object has been moved to wrong position.
        Wrong position: {}
        Right position: {}
        """

        movable_obj = FakeMovableClass(np.array((12, 5)), np.array((-7, 3)))
        MoveCommand(movable_obj).execute()

        self.assertTrue(
            np.array_equal(movable_obj.get_position(), np.array((5, 8))),
            test_fail_msg.format(movable_obj.get_position(), np.array((5, 8)))
        )

    @patch('tests.test_server.test_server.FakeMovableClass.get_position', side_effect=AttributeError())
    def test_trying_move_object_does_not_return_position(self, mock):
        """Check that move command reraise exception if object doesn't have get_position method."""
        movable_obj = FakeMovableClass(np.array((12, 5)), np.array((-7, 3)))
        with self.assertRaises(NotMovableError):
            MoveCommand(movable_obj).execute()

    @patch('tests.test_server.test_server.FakeMovableClass.get_movement_velocity', side_effect=AttributeError())
    def test_trying_move_object_does_not_return_velocity(self, mock):
        """Check that move command reraise exception if object doesn't have get_movement_velocity method."""
        movable_obj = FakeMovableClass(np.array((12, 5)), np.array((-7, 3)))
        with self.assertRaises(NotMovableError):
            MoveCommand(movable_obj).execute()

    @patch('tests.test_server.test_server.FakeMovableClass.set_position', side_effect=AttributeError())
    def test_trying_move_object_does_not_set_position(self, mock):
        """Check that move command reraise exception if object doesn't have set_position method."""
        movable_obj = FakeMovableClass(np.array((12, 5)), np.array((-7, 3)))
        with self.assertRaises(NotMovableError):
            MoveCommand(movable_obj).execute()


class TestRotateCommand(TestCase):
    """Tests for the move command."""

    def test_move(self):
        """
        Test rotate.

        Для объекта c направление 45 градусов и поворачивающегося в лево со скоростью 30 градусов
        финальное направление будет 15 градусов.

        Вектор направления можно будет высчитать позже через матрицу поворота в том месте где это будет необходимо.
        """
        test_fail_msg: str = """
        The object has been rotated to wrong direction.
        Wrong direction: {}
        Right direction: {}
        """
        right_direction: int = 15

        rotable_obj = FakeRotableClass(45, 30)
        RotateCommand(rotable_obj, 'left').execute()

        self.assertEqual(
            rotable_obj.get_direction(), right_direction,
            test_fail_msg.format(rotable_obj.get_direction(), right_direction)
        )

    @patch('tests.test_server.test_server.FakeRotableClass.get_direction', side_effect=AttributeError())
    def test_trying_move_object_does_not_return_direction(self, mock):
        """Check that move command reraise exception if object doesn't have get_direction method."""
        rotable_obj = FakeRotableClass(45, 30)
        with self.assertRaises(NotRotableError):
            RotateCommand(rotable_obj, 'left').execute()

    @patch('tests.test_server.test_server.FakeRotableClass.get_rotation_velocity', side_effect=AttributeError())
    def test_trying_move_object_does_not_return_rotation_velocity(self, mock):
        """Check that move command reraise exception if object doesn't have get_rotation_velocity method."""
        rotable_obj = FakeRotableClass(45, 30)
        with self.assertRaises(NotRotableError):
            RotateCommand(rotable_obj, 'left').execute()

    @patch('tests.test_server.test_server.FakeRotableClass.set_direction', side_effect=AttributeError())
    def test_trying_move_object_does_not_set_direction(self, mock):
        """Check that move command reraise exception if object doesn't have set_direction method."""
        rotable_obj = FakeRotableClass(45, 30)
        with self.assertRaises(NotRotableError):
            RotateCommand(rotable_obj, 'left').execute()
