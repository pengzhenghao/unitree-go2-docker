#!/bin/bash
echo "Setup unitree ros2 environment"
echo "Sourcing ROS2 Foxy"
source /opt/ros/foxy/setup.bash
echo "Sourcing unitree_ros2 workspace"
source /app/unitree_ros2/cyclonedds_ws/install/setup.bash
echo "Setting RMW implementation to CycloneDDS"
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Assert the environment variable is set
if [ -z "${GO2_NETWORK_INTERFACE}" ]; then
    echo "GO2_NETWORK_INTERFACE is not set. Raise an error."
    exit 1
fi
echo "Go2 will use network interface: ${GO2_NETWORK_INTERFACE}"

echo "Setting CycloneDDS URI"
# Use the network interface specified by the user to fill in the CycloneDDS URI
export CYCLONEDDS_URI="<CycloneDDS><Domain><General><Interfaces><NetworkInterface name=\"${GO2_NETWORK_INTERFACE}\" priority=\"default\" multicast=\"default\" /></Interfaces></General></Domain></CycloneDDS>"
