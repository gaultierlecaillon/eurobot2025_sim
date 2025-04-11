"""Constants used throughout the simulation."""
from typing import Tuple

# Map dimensions (in mm)
MAP_WIDTH = 3000
MAP_HEIGHT = 2000

# Scale factor to convert mm to pixels
SCALE = 0.4

# Window dimensions (in pixels)
WINDOW_WIDTH = int(MAP_WIDTH * SCALE)
WINDOW_HEIGHT = int(MAP_HEIGHT * SCALE)

# Robot dimensions (in mm)
ROBOT_WIDTH = 315
ROBOT_HEIGHT = 235

# Robot movement parameters
DEFAULT_SPEED = 500  # mm per second
DEFAULT_ROTATION_SPEED = 90  # degrees per second

# Colors (RGB)
WHITE: Tuple[int, int, int] = (255, 255, 255)
BLACK: Tuple[int, int, int] = (0, 0, 0)
RED: Tuple[int, int, int] = (255, 0, 0)
BLUE: Tuple[int, int, int] = (0, 0, 255)
GREEN: Tuple[int, int, int] = (0, 255, 0)
YELLOW: Tuple[int, int, int] = (255, 255, 0)

# Robot states
IDLE = 0
ROTATING_TO_TARGET = 1
MOVING_FORWARD = 2
FINAL_ROTATION = 3

# Map transparency
MAP_ALPHA = 200

# Frame rate
FPS = 60
