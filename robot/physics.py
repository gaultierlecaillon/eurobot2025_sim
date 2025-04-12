"""Physics engine for robot movement simulation."""
import math
from typing import Tuple, List
from constants import (
    ROBOT_WIDTH,
    DEFAULT_SPEED,
    DEFAULT_ROTATION_SPEED,
    IDLE,
    ROTATING_TO_TARGET,
    MOVING_FORWARD,
    FINAL_ROTATION,
    FPS
)

class Physics:
    def __init__(self, x: float = 0, y: float = 0, angle: float = 0):
        # Position and orientation
        self.x = x
        self.y = y
        self.angle = self._normalize_angle(angle)
        
        # Movement parameters
        self.speed = DEFAULT_SPEED
        self.rotation_speed = DEFAULT_ROTATION_SPEED
        
        # State tracking
        self.state = IDLE
        self.target_x = 0
        self.target_y = 0
        self.target_angle = 0
        self.distance_to_travel = 0
        self.trajectory: List[Tuple[float, float]] = []
        
    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to be between -180 and 180 degrees."""
        angle = angle % 360
        if angle > 180:
            angle -= 360
        return angle
        
    def _get_angle_to_target(self) -> float:
        """Calculate angle to target position."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        target_angle = math.degrees(math.atan2(dx, dy))
        return self._normalize_angle(target_angle)
        
    def _get_distance_to_target(self) -> float:
        """Calculate distance to target position."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        return math.sqrt(dx * dx + dy * dy)
        
    def _rotate_to_angle(self, target_angle: float) -> bool:
        """Rotate robot towards target angle. Returns True if rotation is complete."""
        angle_diff = self._normalize_angle(target_angle - self.angle)
        
        # Calculate maximum rotation for this frame
        max_rotation = self.rotation_speed / FPS
        
        if abs(angle_diff) <= max_rotation:
            self.angle = target_angle
            return True
            
        # Rotate towards target
        if angle_diff > 0:
            self.angle += max_rotation
        else:
            self.angle -= max_rotation
            
        self.angle = self._normalize_angle(self.angle)
        return False
        
    def _move_forward(self, distance: float) -> bool:
        """Move robot forward by specified distance. Returns True if movement is complete."""
        # Calculate maximum movement for this frame
        max_movement = self.speed / FPS
        
        if abs(distance) <= max_movement:
            # Final movement
            angle_rad = math.radians(self.angle)
            self.x += distance * math.sin(angle_rad)
            self.y += distance * math.cos(angle_rad)
            return True
            
        # Partial movement
        movement = max_movement if distance > 0 else -max_movement
        angle_rad = math.radians(self.angle)
        self.x += movement * math.sin(angle_rad)
        self.y += movement * math.cos(angle_rad)
        
        # Add point to trajectory
        self.trajectory.append((self.x, self.y))
        
        # Update remaining distance
        self.distance_to_travel -= movement
        return False
        
    def goto(self, x: float, y: float, angle: float):
        """Start movement to target position and orientation."""
        self.target_x = x
        self.target_y = y
        self.target_angle = self._normalize_angle(angle)
        self.state = ROTATING_TO_TARGET
        self.trajectory = [(self.x, self.y)]
        
    def forward(self, distance: float):
        """Start forward movement by relative distance."""
        self.distance_to_travel = distance
        self.state = MOVING_FORWARD
        self.trajectory = [(self.x, self.y)]
        
    def rotate(self, angle: float):
        """Start rotation by relative angle."""
        self.target_angle = self._normalize_angle(self.angle + angle)
        self.state = FINAL_ROTATION
        
    def update(self) -> bool:
        """Update physics simulation. Returns True if movement is complete."""
        if self.state == IDLE:
            return True
            
        if self.state == ROTATING_TO_TARGET:
            target_angle = self._get_angle_to_target()
            if self._rotate_to_angle(target_angle):
                self.state = MOVING_FORWARD
                self.distance_to_travel = self._get_distance_to_target()
                
        elif self.state == MOVING_FORWARD:
            if self._move_forward(self.distance_to_travel):
                if self.target_angle != self.angle:
                    self.state = FINAL_ROTATION
                else:
                    self.state = IDLE
                    
        elif self.state == FINAL_ROTATION:
            if self._rotate_to_angle(self.target_angle):
                self.state = IDLE
                
        return self.state == IDLE
        
    def get_position(self) -> Tuple[float, float, float]:
        """Get current position and orientation."""
        return self.x, self.y, self.angle
        
    def get_state(self) -> int:
        """Get current movement state."""
        return self.state
        
    def get_trajectory(self) -> List[Tuple[float, float]]:
        """Get movement trajectory points."""
        return self.trajectory
