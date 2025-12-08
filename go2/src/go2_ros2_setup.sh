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
export CYCLONEDDS_URI="<CycloneDDS><Domain><General><NetworkInterfaceAddress>${GO2_NETWORK_INTERFACE}</NetworkInterfaceAddress><AllowMulticast>true</AllowMulticast></General><Discovery><ParticipantIndex>auto</ParticipantIndex><MaxAutoParticipantIndex>100</MaxAutoParticipantIndex><Peers><Peer address=\"192.168.123.18\"/></Peers></Discovery></Domain></CycloneDDS>"

# Add a specific route for the robot subnet if possible (requires privilege, might fail in container but worth a try if host mode)
# route add -net 192.168.123.0 netmask 255.255.255.0 dev ${GO2_NETWORK_INTERFACE} 2>/dev/null || true
