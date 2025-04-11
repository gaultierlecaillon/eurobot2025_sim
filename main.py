"""Main simulation entry point."""
import json
import os
import sys
from typing import Dict, List, Tuple, Union
import pygame

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SCALE,
    BLACK,
    MAP_ALPHA,
    FPS
)
from robot import Robot

class SimulationError(Exception):
    """Base class for simulation errors."""
    pass

class ConfigError(SimulationError):
    """Error in simulation configuration."""
    pass

def validate_strategy(data: Dict) -> None:
    """Validate strategy file format.
    
    Args:
        data: Loaded JSON data
        
    Raises:
        ConfigError: If strategy format is invalid
    """
    required_fields = {"startingPos", "strategy"}
    if not all(field in data for field in required_fields):
        raise ConfigError(
            f"Strategy must contain fields: {', '.join(required_fields)}"
        )
        
    try:
        # Validate starting position format
        x, y, angle = map(float, data["startingPos"].split(","))
    except ValueError:
        raise ConfigError(
            "Starting position must be in format: 'x,y,angle'"
        )
        
    if not isinstance(data["strategy"], list):
        raise ConfigError("Strategy must be a list of action groups")
        
    for group in data["strategy"]:
        if not isinstance(group, dict):
            raise ConfigError("Each strategy group must be an object")
            
        if "name" not in group or "actions" not in group:
            raise ConfigError(
                "Strategy groups must have 'name' and 'actions' fields"
            )
            
        if not isinstance(group["actions"], list):
            raise ConfigError("Group actions must be a list")
            
        for action in group["actions"]:
            if not isinstance(action, dict):
                raise ConfigError("Each action must be an object")
                
            if len(action) != 1:
                raise ConfigError(
                    "Each action must have exactly one command"
                )
                
            cmd = next(iter(action))
            if cmd not in {"goto", "forward"}:
                raise ConfigError(
                    f"Unknown action command: {cmd}"
                )
                
            if cmd == "goto":
                try:
                    x, y, angle = map(
                        float,
                        action[cmd].split(",")
                    )
                except ValueError:
                    raise ConfigError(
                        "Goto command must be in format: 'x,y,angle'"
                    )
            elif cmd == "forward":
                try:
                    distance = float(action[cmd])
                except ValueError:
                    raise ConfigError(
                        "Forward command must be a number"
                    )

class Simulation:
    """Robot movement simulation."""
    
    def __init__(
        self,
        strategy_file: str,
        mode: str = "live",
        speed_multiplier: float = 1.0
    ):
        """Initialize simulation.
        
        Args:
            strategy_file: Path to strategy JSON file
            mode: Simulation mode ('live' or 'instant')
            speed_multiplier: Movement speed multiplier
            
        Raises:
            ConfigError: If configuration is invalid
            pygame.error: If image loading fails
            FileNotFoundError: If files are missing
            json.JSONDecodeError: If strategy file is invalid JSON
        """
        # Validate inputs
        if mode not in {"live", "instant"}:
            raise ConfigError(f"Invalid mode: {mode}")
            
        if speed_multiplier <= 0:
            raise ConfigError("Speed multiplier must be positive")
            
        # Initialize display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Robot Simulation")
        
        # Load and validate files
        if not os.path.exists(strategy_file):
            raise FileNotFoundError(f"Strategy file not found: {strategy_file}")
            
        if not os.path.exists("map.png"):
            raise FileNotFoundError("Map image not found: map.png")
            
        if not os.path.exists("robot.png"):
            raise FileNotFoundError("Robot image not found: robot.png")
        
        # Load map
        self.map_img = pygame.image.load("map.png")
        self.map_img = pygame.transform.scale(
            self.map_img,
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        self.map_img.set_alpha(MAP_ALPHA)
        
        # Load and validate strategy
        with open(strategy_file, 'r') as f:
            self.strategy = json.load(f)
        validate_strategy(self.strategy)
        
        # Create robot
        self.robot = Robot("robot.png", SCALE, speed_multiplier)
        
        # Set initial position
        start_x, start_y, start_angle = map(
            float,
            self.strategy["startingPos"].split(",")
        )
        self.robot.set_position(start_x, start_y, start_angle)
        
        self.mode = mode
        
    def convert_coordinates(self, x: float, y: float) -> Tuple[int, int]:
        """Convert from robot coordinates to screen coordinates.
        
        Origin (0,0) is at bottom center of map
        Positive y is right, negative y is left
        Positive x is up, negative x is down
        
        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            
        Returns:
            Tuple of (screen_x, screen_y) in pixels
        """
        screen_x = WINDOW_WIDTH // 2 + int(y * SCALE)
        screen_y = WINDOW_HEIGHT - int(x * SCALE)
        return screen_x, screen_y
        
    def draw(self) -> None:
        """Draw current simulation state."""
        self.screen.fill(BLACK)
        self.screen.blit(self.map_img, (0, 0))
        self.robot.draw(self.screen, self.convert_coordinates)
        pygame.display.flip()
        
    def run(self) -> None:
        """Run the simulation."""
        running = True
        clock = pygame.time.Clock()
        
        try:
            # Process each action group
            for group in self.strategy["strategy"]:
                for action in group["actions"]:
                    if "goto" in action:
                        x, y, angle = map(float, action["goto"].split(","))
                        self.robot.move_to(x, y, angle)
                    elif "forward" in action:
                        distance = float(action["forward"])
                        self.robot.move_forward(distance)
                        
                    # Update until movement complete
                    if self.mode == "live":
                        while self.robot.is_moving():
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    return
                                    
                            self.robot.update()
                            self.draw()
                            clock.tick(FPS)
                    else:  # instant mode
                        while self.robot.is_moving():
                            self.robot.update()
                        self.draw()
            
            # Keep window open
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        
                clock.tick(FPS)
                
        except Exception as e:
            print(f"\nError during simulation: {e}", file=sys.stderr)
            raise
            
        finally:
            pygame.quit()

def main() -> None:
    """Main entry point."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Parse command line args
        mode = "live" if len(sys.argv) < 2 else sys.argv[1]
        speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
        
        # Run simulation
        sim = Simulation("strategy.json", mode, speed)
        sim.run()
        
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    except ConfigError as e:
        print(f"\nConfiguration error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
