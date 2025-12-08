#!/bin/bash
set -e

# Source the ROS environment
source /opt/ros/foxy/setup.bash

# Ensure CycloneDDS uses our config
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export GO2_NETWORK_INTERFACE=enp118s0

# Source the custom setup script which handles the complex CycloneDDS URI
source /app/src/go2_ros2_setup.sh

# Print an initialization message
echo "Docker container initialized successfully. ROS2 environment is now set up."

# Execute the command passed as arguments (e.g., bash)
exec "$@"