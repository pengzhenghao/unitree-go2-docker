#!/bin/bash
# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Building Go2 Docker image..."
# Build using the script directory as the build context
docker build -t unitree-go2:latest -f "$SCRIPT_DIR/Dockerfile" "$SCRIPT_DIR"
