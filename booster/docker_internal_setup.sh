#!/bin/bash
set -e

echo "Sourcing ROS2 Foxy"
source /opt/ros/foxy/setup.bash

echo "Sourcing Booster ROS 2 workspace"
if [ -f "/app/booster_ws/install/setup.bash" ]; then
    source /app/booster_ws/install/setup.bash
    echo "✓ Booster ROS 2 workspace sourced"
fi

# Print an initialization message
echo "Docker container initialized successfully. ROS2 environment is now set up."

# Execute the command passed as arguments (e.g., bash)
exec "$@"