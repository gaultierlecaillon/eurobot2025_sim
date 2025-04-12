"""Main simulation entry point."""
import sys
import json
import pygame
import pyperclip
from typing import Dict, List, Any
from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BLACK,
    FPS
)
from robot import Robot

def load_strategy(filename: str) -> Dict[str, Any]:
    """Load and validate strategy file."""
    with open(filename, 'r') as f:
        strategy = json.load(f)
        
    # Validate required fields
    required_fields = ['type', 'name', 'color', 'startingPos', 'timer', 'strategy']
    for field in required_fields:
        if field not in strategy:
            raise ValueError(f"Missing required field: {field}")
            
    # Parse starting position
    try:
        x, y, angle = map(float, strategy['startingPos'].split(','))
        print(f"Starting position: x={x} y={y} angle={angle}")
    except ValueError:
        raise ValueError("Invalid starting position format. Expected: 'x,y,angle'")
        
    return strategy

def main():
    # Parse command line arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else 'live'
    speed_multiplier = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Eurobot 2025 Simulation")
    clock = pygame.time.Clock()
    
    # Load strategy
    try:
        strategy = load_strategy('strategies/demo.json')
    except Exception as e:
        print(f"Error loading strategy: {e}")
        return
        
    # Initialize robot
    x, y, angle = map(float, strategy['startingPos'].split(','))
    robot = Robot(screen, x, y, angle)
    
    # Main simulation loop
    current_step = 0
    current_action = 0
    running = True
    movement_complete = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get clicked coordinates and copy to clipboard
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x, world_y = robot.get_world_coordinates(mouse_x, mouse_y)
                coords = f"{world_x:.1f},{world_y:.1f}"
                pyperclip.copy(coords)
                print(f"Copied coordinates: {coords}")
                
        # Process strategy
        if movement_complete and current_step < len(strategy['strategy']):
            step = strategy['strategy'][current_step]
            actions = step['actions']
            
            if current_action < len(actions):
                action = actions[current_action]
                
                # Execute action
                if 'goto' in action:
                    x, y, angle = map(float, action['goto'].split(','))
                    robot.goto(x, y, angle)
                elif 'forward' in action:
                    robot.forward(float(action['forward']))
                elif 'rotate' in action:
                    robot.rotate(float(action['rotate']))
                    
                current_action += 1
                movement_complete = False
            else:
                current_step += 1
                current_action = 0
                
        # Update simulation
        if not movement_complete:
            movement_complete = robot.update()
            
        # Draw
        screen.fill(BLACK)
        robot.draw()
        pygame.display.flip()
        
        # Control frame rate
        if mode == 'live':
            clock.tick(FPS * speed_multiplier)
            
    pygame.quit()

if __name__ == '__main__':
    main()
