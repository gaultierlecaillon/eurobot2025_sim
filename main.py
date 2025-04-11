import pygame
import json
import math
from robot import Robot

# Initialize Pygame
pygame.init()

# Constants
MAP_WIDTH = 3000  # mm
MAP_HEIGHT = 2000  # mm
SCALE = 0.4  # Scale factor to convert mm to pixels

# Calculate window size based on map dimensions and scale
WINDOW_WIDTH = int(MAP_WIDTH * SCALE)
WINDOW_HEIGHT = int(MAP_HEIGHT * SCALE)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Simulation:
    def __init__(self, strategy_file, mode="live", speed_multiplier=1.0):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Robot Simulation")
        
        # Load map and robot images
        self.map_img = pygame.image.load("map.png")
        self.map_img = pygame.transform.scale(self.map_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Create robot instance with speed multiplier
        self.robot = Robot("robot.png", SCALE, speed_multiplier)
        
        # Load strategy
        with open(strategy_file, 'r') as f:
            self.strategy = json.load(f)
        
        # Set initial position
        start_x, start_y, start_angle = map(float, self.strategy["startingPos"].split(","))
        self.robot.set_position(start_x, start_y, start_angle)
        
        self.mode = mode
        self.trajectory = []
        
    def convert_coordinates(self, x, y):
        """Convert from robot coordinates to screen coordinates
        Origin (0,0) is at bottom center of map
        Positive y is right, negative y is left
        Positive x is up, negative x is down
        """
        screen_x = WINDOW_WIDTH // 2 + int(y * SCALE)  # y is positive to the right
        screen_y = WINDOW_HEIGHT - int(x * SCALE)  # Flip x-axis for screen coordinates
        return screen_x, screen_y
        
    def draw(self):
        # Fill background
        self.screen.fill(BLACK)
        
        # Draw robot and its bounding box
        robot_pos = self.convert_coordinates(self.robot.x, self.robot.y)
        pygame.draw.rect(self.screen, RED, 
                        (robot_pos[0] - self.robot.width//2,
                         robot_pos[1] - self.robot.height//2,
                         self.robot.width,
                         self.robot.height), 2)
        self.robot.draw(self.screen, self.convert_coordinates)
        
        # Draw map with some transparency
        self.map_img.set_alpha(200)  # Make map slightly transparent
        self.screen.blit(self.map_img, (0, 0))
        
        # Draw trajectory with different colors based on state
        if len(self.trajectory) > 1:
            points = [self.convert_coordinates(x, y) for x, y, _ in self.trajectory]
            states = [state for _, _, state in self.trajectory]
            
            # Draw lines with different colors based on state
            for i in range(len(points) - 1):
                color = RED  # default
                if states[i] == 1:  # rotating to target
                    color = BLUE
                elif states[i] == 2:  # moving forward
                    color = GREEN
                elif states[i] == 3:  # final rotation
                    color = YELLOW
                pygame.draw.line(self.screen, color, points[i], points[i + 1], 2)
        
        # Draw debug info
        font = pygame.font.Font(None, 36)
        pos_text = font.render(f"Robot: ({int(self.robot.x)}, {int(self.robot.y)}, {int(self.robot.angle)}°)", True, WHITE)
        self.screen.blit(pos_text, (10, 10))
        
        # Draw state info
        state_text = "State: "
        if self.robot.goto_state == 0:
            state_text += "Idle"
        elif self.robot.goto_state == 1:
            state_text += "Rotating to target"
        elif self.robot.goto_state == 2:
            state_text += "Moving forward"
        elif self.robot.goto_state == 3:
            state_text += "Final rotation"
        state_info = font.render(state_text, True, WHITE)
        self.screen.blit(state_info, (10, 50))
        
        pygame.display.flip()
        
    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        # Process each action group in the strategy
        for group in self.strategy["strategy"]:
            for action in group["actions"]:
                if "goto" in action:
                    x, y, angle = map(float, action["goto"].split(","))
                    self.robot.move_to(x, y, angle)
                    if self.mode == "live":
                        while self.robot.is_moving():
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    return
                            
                            self.robot.update()
                            self.trajectory.append((self.robot.x, self.robot.y, self.robot.goto_state))
                            self.draw()
                            clock.tick(60)
                    else:
                        while self.robot.is_moving():
                            self.robot.update()
                            self.trajectory.append((self.robot.x, self.robot.y, self.robot.angle))
                        self.draw()
                
                elif "forward" in action:
                    distance = float(action["forward"])
                    self.robot.move_forward(distance)
                    if self.mode == "live":
                        while self.robot.is_moving():
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    return
                            
                            self.robot.update()
                            self.trajectory.append((self.robot.x, self.robot.y, 0))  # 0 for forward movement
                            self.draw()
                            clock.tick(60)
                    else:
                        while self.robot.is_moving():
                            self.robot.update()
                            self.trajectory.append((self.robot.x, self.robot.y, self.robot.angle))
                        self.draw()
        
        # Keep window open until closed
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    import sys
    try:
        mode = "live" if len(sys.argv) < 2 else sys.argv[1]
        speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
        sim = Simulation("strategy.json", mode, speed)
        sim.run()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
        pygame.quit()
