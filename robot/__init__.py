"""Robot simulation package."""
from dataclasses import dataclass
from typing import Optional, Tuple
import pygame

from .physics import RobotPhysics
from .graphics import RobotGraphics

class Robot:
    """Robot simulation combining physics and graphics."""
    
    def __init__(self, image_path: str, scale: float, speed_multiplier: float = 1.0):
        """Initialize robot simulation.
        
        Args:
            image_path: Path to robot image file
            scale: Scale factor for converting mm to pixels
            speed_multiplier: Multiplier for movement speeds (default: 1.0)
        """
        self.physics = RobotPhysics(speed_multiplier)
        self.graphics = RobotGraphics(image_path)
        
    def set_position(self, x: float, y: float, angle: float) -> None:
        """Set robot position and orientation."""
        self.physics.set_position(x, y, angle)
        
    def move_to(self, x: float, y: float, angle: float) -> None:
        """Move to specified position and orientation."""
        self.physics.move_to(x, y, angle)
        
    def move_forward(self, distance: float) -> None:
        """Move forward by specified distance."""
        self.physics.move_forward(distance)
        
    def rotate(self, angle: float) -> None:
        """Rotate by specified angle.
        
        Args:
            angle: Angle to rotate in degrees
                  Positive = clockwise
                  Negative = counterclockwise
        """
        self.physics.rotate(angle)
        
    def is_moving(self) -> bool:
        """Check if robot is currently moving."""
        return self.physics.is_moving()
        
    def update(self, dt: float = 1/60) -> None:
        """Update robot state.
        
        Args:
            dt: Time step in seconds (default: 1/60)
        """
        self.physics.update(dt)
        if self.is_moving():
            x, y, _ = self.physics.get_position()
            self.graphics.add_trajectory_point(x, y, self.physics.goto_state)
            
    def draw(
        self,
        screen: pygame.Surface,
        convert_coords: callable
    ) -> None:
        """Draw robot and debug information.
        
        Args:
            screen: Pygame surface to draw on
            convert_coords: Function to convert robot to screen coordinates
        """
        x, y, angle = self.physics.get_position()
        self.graphics.draw_robot(screen, x, y, angle, convert_coords)
        self.graphics.draw_trajectory(screen, convert_coords)
        self.graphics.draw_debug_info(screen, x, y, angle, self.physics.goto_state)
