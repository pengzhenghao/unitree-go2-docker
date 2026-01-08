#!/usr/bin/env bash
set -euo pipefail

cd /app

echo "============================================================"
echo "DeepRobotics M20 Pro demo container"
echo "============================================================"
echo "ROBOT_IP=${ROBOT_IP:-<unset>}"
echo "ROBOT_UDP_PORT=${ROBOT_UDP_PORT:-<unset>}"
echo
echo "Quick checks:"
echo "  ip addr"
echo "  ip route"
echo "  ping -c 2 \"\$ROBOT_IP\""
echo
echo "UDP probe:"
echo "  python3 /app/src/udp_probe.py --robot-ip \"\$ROBOT_IP\" --robot-port \"\$ROBOT_UDP_PORT\""
echo "============================================================"

exec "$@"

