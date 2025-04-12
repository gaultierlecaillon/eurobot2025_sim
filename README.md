# Robot Simulation for Eurobot

A 2D simulation to visualize and test robot movements for the Eurobot competition.

## Features

- Real-time visualization of robot movement
- Support for goto and forward commands
- Realistic movement simulation (rotate, move forward, rotate to final angle)
- Visual feedback with colored trajectories:
  - Blue: Robot rotating to face target
  - Green: Moving forward
  - Yellow: Final rotation
  - Red: Direct movement (forward command)

## Usage

```bash
# Run simulation in live mode (default)
python main.py

# Run simulation in instant mode
python main.py instant

# Run simulation with speed multiplier (e.g., 3x speed)
python main.py live 3.0
```

## Strategy File Format

The simulation reads movement commands from a JSON file (`strategies/strategy.json`). Example format:

```json
{
  "startingPos": "x,y,angle",
  "strategy": [
    {
      "name": "Step Name",
      "actions": [
        { "goto": "x,y,angle" },
        { "forward": "distance" }
      ]
    }
  ]
}
```

- `startingPos`: Initial robot position and orientation (x,y,angle in degrees)
- `goto`: Move to coordinates (x,y) and rotate to final angle
- `forward`: Move forward/backward by distance (mm), relative to current orientation

## Map Coordinates

- Origin (0,0) is at the bottom center of the map
- Positive Y is right, negative Y is left
- Positive X is up, negative X is down
- Angles: 0° points right, 90° points up, 180° points left, 270° points down
