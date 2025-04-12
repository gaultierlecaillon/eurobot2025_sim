# Eurobot 2025 Robot Simulation Project

Create a 2D Python simulation for visualizing and testing robot movements for the Eurobot competition. The simulation allows planning and testing robot trajectories with real-time visualization.

## Project Structure

```
eurobot2025_sim/
├── constants.py           # Simulation constants (dimensions, speeds, colors)
├── main.py               # Main simulation entry point
├── robot.py              # Robot class combining physics and graphics
├── img/
│   ├── map.png          # Competition field image
│   ├── playmat_2025_FINAL.png  # Reference playmat image
│   └── robot.png        # Robot sprite image
├── robot/
│   ├── __init__.py
│   ├── physics.py       # Movement physics calculations
│   └── graphics.py      # Pygame visualization
└── strategies/
    ├── demo.json        # Example strategy
    └── strategy.json    # Current strategy file
```

## Dependencies

- Python 3.x
- Pygame library

## Key Features

1. Real-time 2D visualization using Pygame
2. Support for movement commands:
   - goto (x,y,angle): Move to coordinates and rotate to final angle
   - forward (distance): Move forward/backward relative to current orientation
   - rotate (angle): Rotate by relative angle

3. Coordinate System:
   - Origin (0,0) at bottom center of map
   - Positive X is right, negative X is left
   - Positive Y is up, 0 X is down
   - Angles: 0° points up, 90° right, 180° down, 270° left

4. Movement Visualization:
   - Green trajectory: Moving forward
   - Yellow trajectory: Rotation
   - Red trajectory: Direct movement (forward command)
   - Red circle: Robot bounding circle
   - Debug overlay showing position and state

5. Strategy File Format (JSON):
```json
{
  "type": "Strategy",
  "name": "strategy_name",
  "description": "Strategy description",
  "color": "blue|yellow",
  "startingPos": "x,y,angle",
  "timer": "match_duration",
  "strategy": [
    {
      "name": "step_name",
      "actions": [
        { "goto": "x,y,angle" },
        { "forward": "distance" },
        { "rotate": "angle" }
      ]
    }
  ]
}
```

6. Simulation Modes:
   - Live mode: Real-time visualization (default)
   - Instant mode: Skip animations
   - Adjustable speed multiplier

7. Interactive Features:
   - Click on map to get coordinates (auto-copied to clipboard)
   - Visual feedback with trajectory colors
   - Position and state debugging overlay

## Implementation Details

1. Constants (constants.py):
   - Map dimensions: 3000x2000 mm
   - Scale factor: 0.4 (mm to pixels)
   - Robot dimensions: 315x235 mm
   - Default speeds: 500 mm/s, 90 degrees/s
   - FPS: 60

2. Physics Engine (physics.py):
   - Handles position and orientation updates
   - Implements goto sequence: rotate → move → rotate
   - Manages movement state and parameters
   - Normalizes angles and calculates trajectories

3. Graphics Engine (graphics.py):
   - Renders robot sprite with rotation
   - Draws bounding circle and trajectories
   - Color-codes movement states
   - Provides debug information overlay

4. Main Simulation (main.py):
   - Initializes Pygame and simulation
   - Loads and validates strategy file
   - Handles coordinate system conversion
   - Processes movement commands
   - Manages simulation loop and events

## Usage

1. Create strategy file in strategies/ directory
2. Run simulation:
```bash
# Live mode (default)
python main.py

# Instant mode
python main.py instant

# Custom speed (e.g., 3x)
python main.py live 3.0
```

3. Click on map to get coordinates for strategy planning
4. Watch robot execute movements with color-coded trajectories
5. Use debug overlay to monitor position and state

This simulation provides a complete testing environment for Eurobot robot movements, allowing strategy validation and trajectory optimization before physical implementation.
