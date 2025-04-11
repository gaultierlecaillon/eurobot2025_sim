"""Physics engine for robot movement simulation."""
from dataclasses import dataclass
import math
from typing import Optional, Tuple

from constants import DEFAULT_SPEED, DEFAULT_ROTATION_SPEED

@dataclass
class GotoParams:
    """Parameters for a goto movement sequence."""
    target_x: float
    target_y: float
    distance: float
    final_angle: float

class RobotPhysics:
    """Handles robot movement physics and state."""
    
    def __init__(self, speed_multiplier: float = 1.0):
        # Position and orientation
        self.x: float = 0  # mm
        self.y: float = 0  # mm
        self.angle: float = 0  # degrees
        
        # Movement parameters
        self.speed: float = DEFAULT_SPEED * speed_multiplier  # mm per second
        self.rotation_speed: float = DEFAULT_ROTATION_SPEED * speed_multiplier  # degrees per second
        self.target_x: Optional[float] = None
        self.target_y: Optional[float] = None
        self.target_angle: Optional[float] = None
        self.moving: bool = False
        
        # Goto command state
        self.goto_state: int = 0  # Uses constants.IDLE, etc.
        self.goto_params: Optional[GotoParams] = None

    def normalize_angle(self, angle: float) -> float:
        """Normalize angle to be between 0 and 360 degrees."""
        return angle % 360

    def calculate_angle_to_point(self, target_x: float, target_y: float) -> float:
        """Calculate the angle needed to face a target point.
        
        Args:
            target_x: Target x coordinate (horizontal axis, positive right)
            target_y: Target y coordinate (vertical axis, positive up)
            
        Returns:
            Angle in degrees where:
            - 0° points up (positive y)
            - 90° points right (positive x)
            - 180° points down (negative y)
            - 270° points left (negative x)
        """
        dx = target_x - self.x
        dy = target_y - self.y
        # Calculate angle where 0° points up
        angle_to_target = math.degrees(math.atan2(dy, dx))
        return self.normalize_angle(angle_to_target)

    def set_position(self, x: float, y: float, angle: float) -> None:
        """Set the robot's position and orientation."""
        self.x = x
        self.y = y
        self.angle = self.normalize_angle(angle)
        self.target_x = None
        self.target_y = None
        self.target_angle = None
        self.moving = False
        self.goto_state = 0
        self.goto_params = None

    def move_to(self, y: float, x: float, final_angle: float) -> None:
        """Execute a goto command in three steps:
        1. Rotate to face target point
        2. Move forward to target point
        3. Rotate to final angle
        
        Args:
            y: Target y coordinate (vertical axis)
            x: Target x coordinate (horizontal axis)
            final_angle: Final orientation in degrees
        """
        # Calculate distance and angle to target
        dx = x - self.x
        dy = y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        angle_to_target = self.calculate_angle_to_point(x, y)
        
        # Step 1: First rotation - face the target point
        self.target_angle = angle_to_target
        self.target_x = self.x  # Stay in place
        self.target_y = self.y
        self.moving = True
        self.goto_state = 1  # ROTATING_TO_TARGET
        self.goto_params = GotoParams(
            target_x=x,
            target_y=y,
            distance=distance,
            final_angle=self.normalize_angle(final_angle)
        )

    def rotate(self, angle_delta: float) -> None:
        """Rotate the robot by a relative angle.
        
        Args:
            angle_delta: Angle to rotate in degrees
                        Positive = clockwise
                        Negative = counterclockwise
        """
        self.target_angle = self.normalize_angle(self.angle + angle_delta)
        self.target_x = None  # No position movement
        self.target_y = None
        self.moving = True
        self.goto_state = 3  # FINAL_ROTATION - for visualization
        self.goto_params = None

    def move_forward(self, distance: float) -> None:
        """Move forward/backward relative to robot's current orientation.
        
        Positive distance moves in the direction the robot is facing:
        - When angle is 0°, moves up (positive y)
        - When angle is 90°, moves right (positive x)
        - When angle is 180°, moves down (negative y)
        - When angle is 270°, moves left (negative x)
        """
        angle_rad = math.radians(self.angle)  # 0° points up
        # cos for x movement (horizontal), sin for y movement (vertical)
        self.target_x = self.x + distance * math.cos(angle_rad)
        self.target_y = self.y + distance * math.sin(angle_rad)
        self.target_angle = None  # No rotation
        self.moving = True
        self.goto_state = 0  # IDLE - pure movement
        self.goto_params = None

    def is_moving(self) -> bool:
        """Check if the robot is currently in motion."""
        return self.moving

    def get_position(self) -> Tuple[float, float, float]:
        """Get current position and orientation."""
        return self.x, self.y, self.angle

    def update(self, dt: float = 1/60) -> None:
        """Update robot position and orientation based on current movement state.
        
        Args:
            dt: Time step in seconds (default: 1/60 second)
        """
        if not self.moving:
            return

        # Handle rotation
        if self.target_angle is not None:
            # Calculate shortest rotation direction
            angle_diff = (self.target_angle - self.angle + 180) % 360 - 180
            
            if abs(angle_diff) > 0.1:  # Rotation threshold
                # Calculate rotation for this frame
                rotation = min(self.rotation_speed * dt, abs(angle_diff))
                # Update angle
                self.angle = self.normalize_angle(
                    self.angle + math.copysign(rotation, angle_diff)
                )
            else:
                self.angle = self.target_angle
                self.target_angle = None
                
                # If we're in a goto sequence, proceed to next step
                if self.goto_state == 0:  # Pure rotation (not part of goto)
                    self.moving = False
                elif self.goto_state == 1:  # Finished rotating to face target
                    # Start moving forward
                    self.target_x = self.goto_params.target_x
                    self.target_y = self.goto_params.target_y
                    self.goto_state = 2  # MOVING_FORWARD
                elif self.goto_state == 3:  # Finished final rotation
                    self.goto_state = 0  # IDLE
                    self.goto_params = None
                    self.moving = False

        # Handle position movement
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Calculate movement for this frame
                move_distance = min(self.speed * dt, distance)
                # Update position
                self.x += (dx/distance) * move_distance
                self.y += (dy/distance) * move_distance
                
                # If we're close enough to target, snap to it
                if move_distance >= distance:
                    self.x = self.target_x
                    self.y = self.target_y
                    self.target_x = None
                    self.target_y = None
                    
                    # If we're in a goto sequence, proceed to final rotation
                    if self.goto_state == 2:  # MOVING_FORWARD
                        self.target_angle = self.goto_params.final_angle
                        self.goto_state = 3  # FINAL_ROTATION

        # Update moving state
        if self.goto_state == 0:  # IDLE
            self.moving = (self.target_x is not None or self.target_angle is not None)
