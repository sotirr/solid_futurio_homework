"""Commands classes for server module."""
from typing import Literal, Protocol
from abc import ABC, abstractmethod

import numpy as np

from SpaceBattle.server.exceptions import NotMovableError, NotRotableError


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
    def get_position(self) -> np.ndarray:
        """Get current object's position on the map."""
        ...

    @abstractmethod
    def set_position(self, position: np.ndarray) -> None:
        """Set new object's position on the map."""
        ...

    @abstractmethod
    def get_movement_velocity(self) -> np.ndarray:
        """Get object's movement velocity."""
        ...


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
            new_obj_position: np.ndarray = self.obj.get_position() + self.obj.get_movement_velocity()
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
