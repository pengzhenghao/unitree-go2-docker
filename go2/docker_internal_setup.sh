#!/bin/bash
set -e

# Source the ROS environment
source /opt/ros/foxy/setup.bash

# Ensure CycloneDDS uses our config
export CYCLONEDDS_URI=file:///app/unitree_ros2/cyclonedds_ws/src/cyclonedds.xml
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export GO2_NETWORK_INTERFACE=enp118s0

# Print an initialization message
echo "Docker container initialized successfully. ROS2 environment is now set up."

# Execute the command passed as arguments (e.g., bash)
exec "$@"