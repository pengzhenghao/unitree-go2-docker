#!/bin/bash
echo "Setup unitree ros2 environment"
echo "Sourcing ROS2 Foxy"
source /opt/ros/foxy/setup.bash
echo "Sourcing unitree_ros2 workspace"
source /app/unitree_ros2/cyclonedds_ws/install/setup.bash
echo "Setting RMW implementation to CycloneDDS"
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

#export GO2_NETWORK_INTERFACE=eth0
#echo "Go2 will use network interface: ${GO2_NETWORK_INTERFACE}"
echo "Setting CycloneDDS URI"
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces>
                            <NetworkInterface name="eth0" priority="default" multicast="default" />
                        </Interfaces></General></Domain></CycloneDDS>'



RMW_IMPLEMENTATION=rmw_cyclonedds_cpp  ROS_DOMAIN_ID=0   source /opt/ros/foxy/setup.bash