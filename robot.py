import pygame
import math

class Robot:
    def __init__(self, image_path, scale, speed_multiplier=1.0):
        # Load and scale robot image
        self.original_image = pygame.image.load(image_path)
        from constants import ROBOT_WIDTH, ROBOT_HEIGHT, DEFAULT_SPEED, DEFAULT_ROTATION_SPEED
        
        self.width = ROBOT_WIDTH * scale  # mm to pixels
        self.height = ROBOT_HEIGHT * scale  # mm to pixels
        self.image = pygame.transform.scale(self.original_image, (int(self.width), int(self.height)))
        
        # Position and orientation
        self.x = 0  # mm
        self.y = 0  # mm
        self.angle = 0  # degrees
        
        # Movement parameters
        self.speed = DEFAULT_SPEED * speed_multiplier  # mm per second
        self.rotation_speed = DEFAULT_ROTATION_SPEED * speed_multiplier  # degrees per second
        self.target_x = None
        self.target_y = None
        self.target_angle = None
        self.moving = False
        
        # Import states from constants
        from constants import IDLE, ROTATING_TO_TARGET, MOVING_FORWARD, FINAL_ROTATION
        
        # Goto command state
        self.goto_state = IDLE
        self.goto_params = None
        
    def set_position(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.target_x = None
        self.target_y = None
        self.target_angle = None
        self.moving = False
        
    def calculate_angle_to_point(self, target_x, target_y):
        """Calculate the angle needed to face a target point"""
        dx = target_x - self.x
        dy = target_y - self.y
        angle_to_target = math.degrees(math.atan2(dx, dy))  # atan2 returns angle in radians
        return angle_to_target

    def move_to(self, x, y, final_angle):
        """Execute a goto command in three steps:
        1. Rotate to face target point
        2. Move forward to target point
        3. Rotate to final angle
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
        self.goto_state = ROTATING_TO_TARGET
        self.goto_params = {
            'target_x': x,
            'target_y': y,
            'distance': distance,
            'final_angle': final_angle
        }
        
    def move_forward(self, distance):
        """Move forward/backward relative to robot's current orientation
        - When angle is 0, positive distance moves right (positive y)
        - When angle is 90, positive distance moves up (positive x)
        - When angle is 180, positive distance moves left (negative y)
        - When angle is 270, positive distance moves down (negative x)
        """
        angle_rad = math.radians(self.angle)
        # Use negative distance for y when facing left (around 180 degrees)
        # and negative distance for x when facing down (around 270 degrees)
        self.target_x = self.x + distance * math.sin(angle_rad)  # sin for x movement
        self.target_y = self.y + distance * math.cos(angle_rad)  # cos for y movement
        self.target_angle = self.angle
        self.moving = True
        
    def is_moving(self):
        return self.moving
        

    def _update_rotation(self, dt):
        """Handle rotation updates"""
        if self.target_angle is None:
            return False
            
        # Calculate shortest rotation direction
        angle_diff = (self.target_angle - self.angle + 180) % 360 - 180
        
        if abs(angle_diff) > 0.1:
            # Calculate rotation for this frame
            rotation = min(self.rotation_speed * dt, abs(angle_diff))
            # Update angle
            self.angle += math.copysign(rotation, angle_diff)
            return False
        else:
            self.angle = self.target_angle
            self.target_angle = None
            return True
            
    def _update_position(self, dt):
        """Handle position updates"""
        if self.target_x is None or self.target_y is None:
            return False
            
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
                return True
        return False

    def update(self, dt=1/60):
        """Update robot state"""
        if not self.moving:
            return

        # Handle rotation
        if rotation_complete := self._update_rotation(dt):
            # If we're in a goto sequence, proceed to next step
            if self.goto_state == ROTATING_TO_TARGET:
                # Start moving forward
                self.target_x = self.goto_params['target_x']
                self.target_y = self.goto_params['target_y']
                self.goto_state = MOVING_FORWARD
            elif self.goto_state == FINAL_ROTATION:
                self.goto_state = IDLE
                self.goto_params = None
                self.moving = False

        # Handle position movement
        if position_complete := self._update_position(dt):
            # If we're in a goto sequence, proceed to final rotation
            if self.goto_state == MOVING_FORWARD:
                self.target_angle = self.goto_params['final_angle']
                self.goto_state = FINAL_ROTATION

        # Update moving state
        if self.goto_state == IDLE:
            self.moving = (self.target_x is not None or self.target_angle is not None)
        
    def draw(self, screen, convert_coords):
        # Get screen coordinates
        screen_x, screen_y = convert_coords(self.x, self.y)
        
        # Rotate image
        rotated_image = pygame.transform.rotate(self.image, -self.angle)  # Negative because pygame rotation is clockwise
        
        # Get the rect of the rotated image and center it
        rect = rotated_image.get_rect()
        rect.center = (screen_x, screen_y)
        
        # Draw the robot
        screen.blit(rotated_image, rect)
