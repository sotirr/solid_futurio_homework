"""Commands classes for server module."""
from collections import deque
from typing import Any, Literal, Protocol
from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray

from SpaceBattle.server.exceptions import NotMovableError, NotRotableError


class UObject(Protocol):
    """Contract for any game objects."""

    @abstractmethod
    def get_value(self, property: str) -> Any:
        """Get object property's value."""
        ...

    @abstractmethod
    def set_value(self, property: str, value: Any) -> None:
        """Set object property's value."""
        ...

    @abstractmethod
    def del_value(self, property: str) -> None:
        """Del object property."""
        ...


class Command(ABC):
    """Abstract class for command pattern."""

    @abstractmethod
    def execute(self) -> None:
        """
        Contain all logic.

        The only one public method.
        """
        ...


class Movable(Protocol):
    """Contract for movable objects."""

    @abstractmethod
    def get_position(self) -> NDArray[np.float_]:
        """Get current object's position on the map."""
        ...

    @abstractmethod
    def set_position(self, position: NDArray[np.float_]) -> None:
        """Set new object's position on the map."""
        ...

    @abstractmethod
    def get_movement_velocity(self) -> NDArray[np.float_]:
        """Get object's movement velocity."""
        ...


class MovableAdapter:
    """Adapter for change velocity."""

    def __init__(self, obj: UObject) -> None:
        """Init variabels."""
        self.obj = obj

    def get_position(self) -> NDArray[np.float_]:
        """Get current object's position on the map."""
        obj_position: NDArray[np.float_] = self.obj.get_value('position')
        return obj_position

    def set_position(self, position: NDArray[np.float_]) -> None:
        """Set new object's position on the map."""
        return self.obj.set_value('position', position)

    def get_movement_velocity(self) -> NDArray[np.float_]:
        """Get object's movement velocity."""
        movement_velocity: NDArray[np.float_] = self.obj.get_value('velocity')
        return movement_velocity


class MoveCommand(Command):
    """Moves the object on the map."""

    def __init__(self, obj: Movable) -> None:
        """
        Init variabels.

        object - any movable GameObject.
        """
        self.obj = obj
        super().__init__()

    def execute(self) -> None:
        """Run command."""
        try:
            new_obj_position: NDArray[np.float_] = self.obj.get_position() + self.obj.get_movement_velocity()
            self.obj.set_position(new_obj_position)
        except AttributeError as err:
            raise NotMovableError(f'The object cannot be moved. {err}')


class Rotable(Protocol):
    """Contract for movable objects."""

    @abstractmethod
    def get_direction(self) -> int:
        """Retrun object's current direction in degrees range from -360 to +360."""
        ...

    @abstractmethod
    def get_rotation_velocity(self) -> int:
        """Retrun object rotation velocity in degrees range from -360 to +360."""
        ...

    @abstractmethod
    def set_direction(self, direction: int) -> None:
        """Set a new object's direction."""
        ...


class RotateCommand(Command):
    """Rotate the object on the map."""

    def __init__(self, obj: Rotable, direction: Literal['left', 'right']) -> None:
        """
        Init variabels.

        object - any movable GameObject.
        """
        self.obj = obj
        self.direction = direction
        super().__init__()

    def execute(self) -> None:
        """Run command."""
        try:
            if self.direction == 'left':
                new_rotation = self.obj.get_direction() - self.obj.get_rotation_velocity()
            else:
                new_rotation = self.obj.get_direction() + self.obj.get_rotation_velocity()
            self.obj.set_direction(new_rotation)
        except AttributeError as err:
            raise NotRotableError(f'The object cannot be rotated. {err}')


class VelocityChangable(Protocol):
    """Contract for velocity changable object."""

    def set_velocity(self, value: int) -> None:
        """Set velocity to object."""
        ...


class VelocityChangeAdapter:
    """Adapter for change velocity."""

    def __init__(self, obj: UObject) -> None:
        """
        Init variabels.

        Args:
            obj (UObject): object.
        """
        self.obj = obj

    def set_velocity(self, value: int) -> None:
        """Set velocity to object."""
        self.obj.set_value('velocity', value)


class ChangeVelocityCommand(Command):
    """Command for change object velocity."""

    def __init__(self, obj: VelocityChangable, velocity: int) -> None:
        """
        Init variabels.

        object - movable .
        """
        self.obj = obj
        self.velocity = velocity
        super().__init__()

    def execute(self) -> None:
        """Run command."""
        self.obj.set_velocity(self.velocity)


class MoveCommandStartable(Protocol):
    """
    Контракт для управляющего объекта приказа на начало движения.

    {
        “id”: “уникальный идентификатор объекта, которому отдан приказ”,
        “action”: “код операции”, //например, “startMove”, “stopMove”, “fire” и т.д.
        // параметры, специфичные для самого приказа
        “velocity”: 2
    }
    """

    @abstractmethod
    def get_target_object(self) -> UObject:
        """Возвращает объект который будет двигаться по прямой."""
        ...

    @abstractmethod
    def get_target_start_velocity(self) -> int:
        """Возвращает модуль мгновенной скорости с которой начинает двигаться объект."""
        ...

    @abstractmethod
    def get_target_command_queue(self) -> deque[Command]:
        """Возвращает очередь команд, куда будет записана команда созданная команда Move."""
        ...


class StartMoveCommand(Command):
    """Назначает комманду move на выполнение."""

    def __init__(self, order_to_move: MoveCommandStartable) -> None:
        """
        Init variabels.

        Args:
            order_to_move (MoveCommandStartable): объект реализующий приказ на движение
        """
        self.order_to_move = order_to_move

    def execute(self) -> None:
        """Run."""
        self._get_obj()
        self._set_velocity_to_obj()
        self._create_move_command()
        self._add_command_to_target_commands_queue()

    def _get_obj(self) -> None:
        """Get target UObject object."""
        self.obj: UObject = self.order_to_move.get_target_object()

    def _set_velocity_to_obj(self) -> None:
        """Записывает значение скорости в движущийся объект."""
        ChangeVelocityCommand(
            VelocityChangeAdapter(self.obj),
            self.order_to_move.get_target_start_velocity(),
        ).execute()

    def _create_move_command(self) -> None:
        """Create move command."""
        self.move_command = MoveCommand(
            MovableAdapter(self.obj),
        )

    def _add_command_to_target_commands_queue(self) -> None:
        """Add move command to the target commands queue."""
        queue = self.order_to_move.get_target_command_queue()
        queue.append(self.move_command)


class MoveCommandEndable(Protocol):
    """
    Контракт для управляющего объекта приказа на завершение движения.

    {
        “id”: “уникальный идентификатор объекта, которому отдан приказ”,
        “action”: “код операции”, //например, “startMove”, “stopMove”, “fire” и т.д.
        // параметры, специфичные для самого приказа
        “velocity”: 2
    }
    """

    @abstractmethod
    def get_target_move_command(self) -> MoveCommand:
        """Возвращает команду Move, которую необходимо завершить."""
        ...

    @abstractmethod
    def get_target_moveing_object(self) -> UObject:
        """Возвращает объект, который движется с помощью данной команды."""
        ...

    @abstractmethod
    def get_target_commands_queue(self) -> deque[Command]:
        """Возвращает очередь команд Queue<Command>."""
        ...


class VelocityDeletable(Protocol):
    """Contract for velocity deletable object."""

    def del_velocity(self) -> None:
        """Del velocity from object."""
        ...


class VelocityDeletableAdapter:
    """Adapter for delete velocity."""

    def __init__(self, obj: UObject) -> None:
        """
        Init variabels.

        Args:
            obj (UObject): object.
        """
        self.obj = obj

    def del_velocity(self) -> None:
        """Del velocity from object."""
        self.obj.del_value('velocity')


class DeleteVelocityCommand(Command):
    """Command for delete object velocity."""

    def __init__(self, obj: VelocityDeletable) -> None:
        """
        Init variabels.

        object - VelocityDeletable.
        """
        self.obj = obj
        super().__init__()

    def execute(self) -> None:
        """Run command."""
        self.obj.del_velocity()


class EndMoveCommand(Command):
    """Управляющая команда  которая снимает комманду move с выполнения."""

    def __init__(self, order_to_end_move: MoveCommandEndable) -> None:
        """
        Init variabels.

        Args:
            order_to_move (MoveCommandStartable): объект реализующий приказ на движение
        """
        self.order_to_end_move = order_to_end_move

    def execute(self) -> None:
        """Run command."""
        self._erase_velocity_from_target_object()
        self._del_command_from_target_queue()

    def _erase_velocity_from_target_object(self) -> None:
        """
        Удаляет значение скорости из движущегося объекта.

        !Указание. Самая простая реализация потребует добавление в интерфейс UObject метода,
        который удаляет значение по ключу. Вообще, это является нарушением OCP, но предлагаю сделать сейчас так,
        чтобы не усложнять понимание всего процесса работы с SOLID на данном этапе обучения.
        """
        target_obj: UObject = self.order_to_end_move.get_target_moveing_object()
        DeleteVelocityCommand(
            VelocityDeletableAdapter(target_obj),
        )

    def _del_command_from_target_queue(self) -> None:
        """
        Удаляет команду Move из Очереди команд.

        !Указание. Это не самый оптимальный вариант реализации, так как потребует просматривать команды,
        которые находятся в очереди и временные затраты на эту операцию будут пропорциональны длине очереди.
        """
        target_queue: deque[Command] = self.order_to_end_move.get_target_commands_queue()
        move_command: MoveCommand = self.order_to_end_move.get_target_move_command()
        try:
            target_queue.remove(move_command)
        except ValueError:
            pass
