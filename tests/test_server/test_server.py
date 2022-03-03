"""Tests for server module."""
from collections import deque
from unittest import TestCase
from unittest.mock import Mock, create_autospec

import numpy as np
from numpy.typing import NDArray

from SpaceBattle.server.exceptions import NotMovableError, NotRotableError
from SpaceBattle.server.commands import (
    ChangeVelocityCommand, Command, DeleteVelocityCommand, EndMoveCommand, Movable,
    MoveCommand, MoveCommandEndable, MoveCommandStartable, Rotable, RotateCommand,
    StartMoveCommand, VelocityChangable, VelocityDeletable,
)


class TestMoveCommand(TestCase):
    """Tests for the move command."""

    def setUp(self) -> None:
        """Set up the test fixture before exercising it."""
        self.fake_movable_obj = create_autospec(Movable, spec_set=True, instance=True)
        return super().setUp()

    def test_move(self) -> None:
        """
        Test move.

        Для объекта, находящегося в точке (12, 5) и движущегося со скоростью (-7, 3)
        движение меняет положение объекта на (5, 8).
        """
        self.fake_movable_obj.get_position.return_value = np.array((12, 5))
        self.fake_movable_obj.get_movement_velocity.return_value = np.array((-7, 3))
        MoveCommand(self.fake_movable_obj).execute()

        self.fake_movable_obj.set_position.assert_called_once()
        new_position = self.fake_movable_obj.set_position.call_args.args[0]
        expecting_position: NDArray[np.float_] = np.array((5, 8))
        np.testing.assert_array_equal(
            new_position, expecting_position,
            err_msg='The object has been moved to wrong position.',
        )

    def test_trying_move_object_does_not_return_position(self) -> None:
        """Check that move command reraise exception if object raise exception in get_position method."""
        self.fake_movable_obj.get_position.side_effect = Exception('Boom!')
        with self.assertRaises(NotMovableError):
            MoveCommand(self.fake_movable_obj).execute()

    def test_trying_move_object_does_not_return_velocity(self) -> None:
        """Check that move command reraise exception if object raise exception in get_movement_velocity method."""
        self.fake_movable_obj.get_movement_velocity.side_effect = Exception('Boom!')
        with self.assertRaises(NotMovableError):
            MoveCommand(self.fake_movable_obj).execute()

    def test_trying_move_object_does_not_set_position(self) -> None:
        """Check that move command reraise exception if object raise exception in set_position method."""
        self.fake_movable_obj.set_position.side_effect = Exception('Boom!')
        with self.assertRaises(NotMovableError):
            MoveCommand(self.fake_movable_obj).execute()


class TestRotateCommand(TestCase):
    """Tests for the move command."""

    def setUp(self) -> None:
        """Set up the test fixture before exercising it."""
        self.fake_rotable_obj = create_autospec(Rotable, spec_set=True, instance=True)
        return super().setUp()

    def test_left_rotate(self) -> None:
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

        self.fake_rotable_obj.get_direction.return_value = 45
        self.fake_rotable_obj.get_rotation_velocity.return_value = 30
        RotateCommand(self.fake_rotable_obj, 'left').execute()

        self.fake_rotable_obj.set_direction.assert_called_once()
        new_direction = self.fake_rotable_obj.set_direction.call_args.args[0]
        expect_direction: int = 15

        self.assertEqual(
            new_direction, expect_direction,
            test_fail_msg.format(new_direction, expect_direction),
        )

    def test_right_rotate(self) -> None:
        """
        Test rotate.

        Для объекта c направление 45 градусов и поворачивающегося в право со скоростью 30 градусов
        финальное направление будет 75 градусов.

        Вектор направления можно будет высчитать позже через матрицу поворота в том месте где это будет необходимо.
        """
        test_fail_msg: str = """
        The object has been rotated to wrong direction.
        Wrong direction: {}
        Right direction: {}
        """

        self.fake_rotable_obj.get_direction.return_value = 45
        self.fake_rotable_obj.get_rotation_velocity.return_value = 30
        RotateCommand(self.fake_rotable_obj, 'right').execute()

        self.fake_rotable_obj.set_direction.assert_called_once()
        new_direction = self.fake_rotable_obj.set_direction.call_args.args[0]
        expect_direction: int = 75

        self.assertEqual(
            new_direction, expect_direction,
            test_fail_msg.format(new_direction, expect_direction),
        )

    def test_trying_move_object_does_not_return_direction(self) -> None:
        """Check that move command reraise exception if object raise exception in get_direction method."""
        self.fake_rotable_obj.get_direction.side_effect = Exception('Boom!')
        with self.assertRaises(NotRotableError):
            RotateCommand(self.fake_rotable_obj, 'left').execute()

    def test_trying_move_object_does_not_return_rotation_velocity(self) -> None:
        """Check that move command reraise exception if object raise exception in get_rotation_velocity method."""
        self.fake_rotable_obj.get_rotation_velocity.side_effect = Exception('Boom!')
        with self.assertRaises(NotRotableError):
            RotateCommand(self.fake_rotable_obj, 'left').execute()

    def test_trying_move_object_does_not_set_direction(self) -> None:
        """Check that move command reraise exception if object raise exception in set_direction method."""
        self.fake_rotable_obj.set_direction.side_effect = Exception('Boom!')
        with self.assertRaises(NotRotableError):
            RotateCommand(self.fake_rotable_obj, 'left').execute()


class TestChangeVelocityCommand(TestCase):
    """Tests for the ChangeVelocityCommand class."""

    def setUp(self) -> None:
        """Set up the test fixture before exercising it."""
        self.fake_velocity_changable_obj = create_autospec(VelocityChangable, spec_set=True, instance=True)
        return super().setUp()

    def test_change_velocity(self) -> None:
        """Check that command changed object's velocity."""
        ChangeVelocityCommand(self.fake_velocity_changable_obj, 5).execute()

        self.fake_velocity_changable_obj.set_velocity.assert_called_once()

        velocity_new = self.fake_velocity_changable_obj.set_velocity.call_args.args[0]
        velocity_expect = 5
        self.assertEqual(velocity_new, velocity_expect)

    def test_object_can_not_set_position(self) -> None:
        """Check that command reraise exception if object raise exception in set_velocity method."""
        self.fake_velocity_changable_obj.set_velocity.side_effect = Exception('Boom!')
        with self.assertRaises(Exception):
            MoveCommand(self.fake_velocity_changable_obj).execute()


class TestDeleteVelocityCommand(TestCase):
    """Tests for the DeleteVelocityCommand class."""

    def setUp(self) -> None:
        """Set up the test fixture before exercising it."""
        self.fake_velocity_deletable_obj = create_autospec(VelocityDeletable, spec_set=True, instance=True)
        return super().setUp()

    def test_del_velocity(self) -> None:
        """Check that command delete object's velocity."""
        DeleteVelocityCommand(self.fake_velocity_deletable_obj).execute()

        self.fake_velocity_deletable_obj.del_velocity.assert_called_once()

    def test_object_can_not_del_velocity(self) -> None:
        """Check that command reraise exception if object raise exception in set_velocity method."""
        self.fake_velocity_deletable_obj.del_velocity.side_effect = Exception('Boom!')
        with self.assertRaises(Exception):
            DeleteVelocityCommand(self.fake_velocity_deletable_obj).execute()


class TestStartMoveCommand(TestCase):
    """Tests for StartMoveCommand class."""

    def setUp(self) -> None:
        """Set up the test fixture before exercising it."""
        self.fake_order_obj = create_autospec(MoveCommandStartable, spec_set=True, instance=True)
        self.fake_order_obj.get_target_object.return_value = Mock()
        self.fake_order_obj.get_target_start_velocity.return_value = 5
        self.fake_order_obj.get_target_command_queue.return_value = deque()
        return super().setUp()

    def test_add_command_to_queue(self) -> None:
        """Checks that command was added to queue."""
        StartMoveCommand(self.fake_order_obj).execute()

        command_in_queue = self.fake_order_obj.get_target_command_queue().pop()

        self.assertIsInstance(command_in_queue, Command)

    def test_add_property_to_obj(self) -> None:
        """Check that property was added to Object."""
        StartMoveCommand(self.fake_order_obj).execute()

        fake_object = self.fake_order_obj.get_target_object()

        fake_object.set_value.assert_called_once()

        property_set = fake_object.set_value.call_args.args
        property_expecting = ('velocity', 5)

        self.assertEqual(property_set, property_expecting, 'Order command set wrong property value to the object.')

    def test_reraise_error_if_get_target_object_raise_error(self) -> None:
        """Check that command reraise exception if object raise exception in get_target_object method."""
        self.fake_order_obj.get_target_object.side_effect = Exception('Boom!')
        with self.assertRaises(Exception):
            StartMoveCommand(self.fake_order_obj).execute()

    def test_reraise_error_if_get_target_start_velocity_raise_error(self) -> None:
        """Check that command reraise exception if object raise exception in get_target_start_velocity method."""
        self.fake_order_obj.get_target_start_velocity.side_effect = Exception('Boom!')
        with self.assertRaises(Exception):
            StartMoveCommand(self.fake_order_obj).execute()

    def test_reraise_error_if_get_target_command_queue_raise_error(self) -> None:
        """Check that command reraise exception if object raise exception in get_target_command_queue method."""
        self.fake_order_obj.get_target_command_queue.side_effect = Exception('Boom!')
        with self.assertRaises(Exception):
            StartMoveCommand(self.fake_order_obj).execute()


class TestEndMoveCommand(TestCase):
    """Tests for EndMoveCommand class."""

    def setUp(self) -> None:
        """Set up the test fixture before exercising it."""
        self.fake_order_obj = create_autospec(MoveCommandEndable, spec_set=True, instance=True)
        target_command = Mock()
        self.command_queue: deque[Mock] = deque()
        self.command_queue.append(target_command)
        self.fake_order_obj.get_target_moveing_object.return_value = Mock()
        self.fake_order_obj.get_target_move_command.return_value = target_command
        self.fake_order_obj.get_target_commands_queue.return_value = self.command_queue
        return super().setUp()

    def test_dell_command_from_queue(self) -> None:
        """Checks that command was deleted from queue."""
        EndMoveCommand(self.fake_order_obj).execute()
        self.assertTrue(len(self.command_queue) == 0, "Command was not deleted from queue!")

    def test_del_property_from_obj(self) -> None:
        """Check that property was deleted from Object."""
        EndMoveCommand(self.fake_order_obj).execute()

        fake_object = self.fake_order_obj.get_target_moveing_object()

        fake_object.del_value.assert_called_once()

        property_send = fake_object.del_value.call_args.args
        property_expecting = ('velocity',)

        self.assertEqual(property_send, property_expecting, "Order command don't del property from the object.")

    def test_reraise_error_if_get_target_moveing_object_raise_error(self) -> None:
        """Check that command reraise exception if object raise exception in get_target_moveing_object method."""
        self.fake_order_obj.get_target_moveing_object.side_effect = Exception('Boom!')
        with self.assertRaises(Exception):
            EndMoveCommand(self.fake_order_obj).execute()

    def test_reraise_error_if_get_target_commands_queue_raise_error(self) -> None:
        """Check that command reraise exception if object raise exception in get_target_commands_queue method."""
        self.fake_order_obj.get_target_commands_queue.side_effect = Exception('Boom!')
        with self.assertRaises(Exception):
            EndMoveCommand(self.fake_order_obj).execute()

    def test_reraise_error_if_get_target_move_command_raise_error(self) -> None:
        """Check that command reraise exception if object raise exception in get_target_move_command method."""
        self.fake_order_obj.get_target_move_command.side_effect = Exception('Boom!')
        with self.assertRaises(Exception):
            EndMoveCommand(self.fake_order_obj).execute()
