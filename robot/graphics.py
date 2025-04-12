"""Graphics engine for robot visualization using Pygame."""
import math
import pygame
from typing import Tuple, List
from constants import (
    SCALE,
    ROBOT_WIDTH,
    ROBOT_HEIGHT,
    CIRCLE_MARGIN,
    TRAJECTORY_POINT_RADIUS,
    WHITE,
    BLACK,
    RED,
    GREEN,
    YELLOW,
    ROTATING_TO_TARGET,
    MOVING_FORWARD,
    FINAL_ROTATION,
    MAP_ALPHA,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)

class Graphics:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        
        # Load and scale robot sprite
        self.robot_sprite = pygame.image.load("img/robot.png")
        scaled_width = int(ROBOT_WIDTH * SCALE)
        scaled_height = int(ROBOT_HEIGHT * SCALE)
        self.robot_sprite = pygame.transform.scale(self.robot_sprite, (scaled_width, scaled_height))
        
        # Load and scale map
        self.map_surface = pygame.image.load("img/map.png")
        self.map_surface = pygame.transform.scale(self.map_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.map_surface.set_alpha(MAP_ALPHA)
        
    def _world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        screen_x = int(x * SCALE + self.screen.get_width() / 2)
        screen_y = int(self.screen.get_height() - y * SCALE)
        return screen_x, screen_y
        
    def _draw_circle(self, x: float, y: float, radius: float, color: Tuple[int, int, int]):
        """Draw circle at world coordinates."""
        screen_x, screen_y = self._world_to_screen(x, y)
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), int(radius * SCALE))
        
    def _draw_trajectory(self, trajectory: List[Tuple[float, float]], color: Tuple[int, int, int]):
        """Draw movement trajectory."""
        if len(trajectory) < 2:
            return
            
        # Convert trajectory points to screen coordinates
        screen_points = [self._world_to_screen(x, y) for x, y in trajectory]
        
        # Draw lines connecting points
        pygame.draw.lines(self.screen, color, False, screen_points, 2)
        
        # Draw points
        for point in screen_points:
            pygame.draw.circle(self.screen, color, point, TRAJECTORY_POINT_RADIUS)
            
    def draw(self, x: float, y: float, angle: float, state: int, trajectory: List[Tuple[float, float]]):
        """Draw robot and visualization elements."""
        # Draw map
        self.screen.blit(self.map_surface, (0, 0))
        
        # Draw bounding circle
        circle_radius = (ROBOT_WIDTH + CIRCLE_MARGIN) / 2
        self._draw_circle(x, y, circle_radius, RED)
        
        # Draw trajectory with color based on state
        if state == ROTATING_TO_TARGET:
            trajectory_color = YELLOW
        elif state == MOVING_FORWARD:
            trajectory_color = GREEN
        elif state == FINAL_ROTATION:
            trajectory_color = RED
        else:
            trajectory_color = WHITE
            
        self._draw_trajectory(trajectory, trajectory_color)
        
        # Draw robot sprite
        screen_x, screen_y = self._world_to_screen(x, y)
        rotated_sprite = pygame.transform.rotate(self.robot_sprite, -angle)  # Negative angle for clockwise rotation
        sprite_rect = rotated_sprite.get_rect(center=(screen_x, screen_y))
        self.screen.blit(rotated_sprite, sprite_rect)
        
        # Draw debug info
        debug_text = f"X: {x:.1f} Y: {y:.1f} Angle: {angle:.1f}°"
        text_surface = self.font.render(debug_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))
        
    def get_world_coordinates(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = (screen_x - self.screen.get_width() / 2) / SCALE
        world_y = (self.screen.get_height() - screen_y) / SCALE
        return world_x, world_y
