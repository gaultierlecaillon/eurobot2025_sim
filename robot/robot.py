"""Main robot class combining physics and graphics components."""
import pygame
from robot.physics import Physics
from robot.graphics import Graphics

class Robot:
    def __init__(self, screen: pygame.Surface, x: float = 0, y: float = 0, angle: float = 0):
        """Initialize robot with physics and graphics engines."""
        self.physics = Physics(x, y, angle)
        self.graphics = Graphics(screen)
        
    def goto(self, x: float, y: float, angle: float):
        """Move to absolute position and orientation."""
        self.physics.goto(x, y, angle)
        
    def forward(self, distance: float):
        """Move forward by relative distance."""
        self.physics.forward(distance)
        
    def rotate(self, angle: float):
        """Rotate by relative angle."""
        self.physics.rotate(angle)
        
    def update(self) -> bool:
        """Update robot state. Returns True if movement is complete."""
        return self.physics.update()
        
    def draw(self):
        """Draw robot and visualization elements."""
        x, y, angle = self.physics.get_position()
        state = self.physics.get_state()
        trajectory = self.physics.get_trajectory()
        self.graphics.draw(x, y, angle, state, trajectory)
        
    def get_world_coordinates(self, screen_x: int, screen_y: int):
        """Convert screen coordinates to world coordinates."""
        return self.graphics.get_world_coordinates(screen_x, screen_y)
