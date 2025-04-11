"""Graphics rendering for robot visualization."""
from dataclasses import dataclass
from typing import Callable, List, Tuple
import pygame

from constants import (
    ROBOT_WIDTH,
    ROBOT_HEIGHT,
    SCALE,
    RED,
    BLUE,
    GREEN,
    YELLOW,
    ROTATING_TO_TARGET,
    MOVING_FORWARD,
    FINAL_ROTATION
)

@dataclass
class TrajectoryPoint:
    """A point in the robot's trajectory with position and state."""
    x: float
    y: float
    state: int

class RobotGraphics:
    """Handles robot visualization and trajectory drawing."""
    
    def __init__(self, image_path: str):
        """Initialize robot graphics.
        
        Args:
            image_path: Path to robot image file
        """
        # Load and scale robot image
        self.original_image = pygame.image.load(image_path)
        self.width = int(ROBOT_WIDTH * SCALE)
        self.height = int(ROBOT_HEIGHT * SCALE)
        self.image = pygame.transform.scale(
            self.original_image, 
            (self.width, self.height)
        )
        
        # Trajectory history
        self.trajectory: List[TrajectoryPoint] = []

    def add_trajectory_point(self, x: float, y: float, state: int) -> None:
        """Add a point to the trajectory history."""
        self.trajectory.append(TrajectoryPoint(x, y, state))

    def draw_robot(
        self,
        screen: pygame.Surface,
        x: float,
        y: float,
        angle: float,
        convert_coords: Callable[[float, float], Tuple[int, int]]
    ) -> None:
        """Draw the robot at the specified position and orientation.
        
        Args:
            screen: Pygame surface to draw on
            x: Robot x position in mm
            y: Robot y position in mm
            angle: Robot angle in degrees
            convert_coords: Function to convert from robot to screen coordinates
        """
        # Get screen coordinates
        screen_x, screen_y = convert_coords(x, y)
        
        # Draw bounding box
        pygame.draw.rect(
            screen,
            RED, 
            (
                screen_x - self.width//2,
                screen_y - self.height//2,
                self.width,
                self.height
            ),
            2
        )
        
        # Rotate and draw robot image
        rotated_image = pygame.transform.rotate(
            self.image,
            -angle  # Negative because pygame rotation is clockwise
        )
        rect = rotated_image.get_rect()
        rect.center = (screen_x, screen_y)
        screen.blit(rotated_image, rect)

    def draw_trajectory(
        self,
        screen: pygame.Surface,
        convert_coords: Callable[[float, float], Tuple[int, int]]
    ) -> None:
        """Draw the robot's movement trajectory with state-based colors.
        
        Args:
            screen: Pygame surface to draw on
            convert_coords: Function to convert from robot to screen coordinates
        """
        if len(self.trajectory) < 2:
            return

        points = [
            convert_coords(point.x, point.y)
            for point in self.trajectory
        ]
        
        # Draw lines with different colors based on state
        for i in range(len(points) - 1):
            color = RED  # default color
            state = self.trajectory[i].state
            
            if state == ROTATING_TO_TARGET:
                color = BLUE
            elif state == MOVING_FORWARD:
                color = GREEN
            elif state == FINAL_ROTATION:
                color = YELLOW
                
            pygame.draw.line(
                screen,
                color,
                points[i],
                points[i + 1],
                2
            )

    def draw_debug_info(
        self,
        screen: pygame.Surface,
        x: float,
        y: float,
        angle: float,
        state: int
    ) -> None:
        """Draw debug information overlay.
        
        Args:
            screen: Pygame surface to draw on
            x: Robot x position in mm
            y: Robot y position in mm
            angle: Robot angle in degrees
            state: Current robot state
        """
        font = pygame.font.Font(None, 36)
        
        # Position info
        pos_text = font.render(
            f"Robot: ({int(x)}, {int(y)}, {int(angle)}°)",
            True,
            (255, 255, 255)
        )
        screen.blit(pos_text, (10, 10))
        
        # State info
        state_text = "State: "
        if state == 0:
            state_text += "Idle"
        elif state == ROTATING_TO_TARGET:
            state_text += "Rotating to target"
        elif state == MOVING_FORWARD:
            state_text += "Moving forward"
        elif state == FINAL_ROTATION:
            state_text += "Final rotation"
            
        state_info = font.render(
            state_text,
            True,
            (255, 255, 255)
        )
        screen.blit(state_info, (10, 50))
