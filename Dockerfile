# Use the official ROS Foxy Desktop image as a base (Ubuntu 20.04)
FROM osrf/ros:foxy-desktop

# Set an environment variable for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install additional packages (e.g., pip and other tools)
RUN apt-get update && apt-get install -y \
    python3-pip \
    iputils-ping \
    git \
    vim \
    ros-foxy-rmw-cyclonedds-cpp \
    ros-foxy-rosidl-generator-dds-idl \
    && rm -rf /var/lib/apt/lists/*

# Copy your entire repository into the container
COPY . /app


# ===== Installing unitree_sdk2 =====
# Build the Unitree SDK:
# Change to the unitree_sdk2 folder, make install.sh executable and run it,
# then create a build directory, run cmake and make.
WORKDIR /app/unitree_sdk2
RUN mkdir build && \
    cd build && \
    cmake .. && \
    sudo make install
# ===== Installing unitree_sdk2 =====


# ===== Installing unitree_ros2 =====
# Following https://github.com/unitreerobotics/unitree_ros2
# To get unitree_ros2 installed.
WORKDIR /app/unitree_ros2/cyclonedds_ws/src
RUN git clone https://github.com/ros2/rmw_cyclonedds -b foxy && \
    git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x && \
    cd .. && \
    colcon build --packages-select cyclonedds
# Now, source the ROS2 environment and build the rest of the packages,
# skipping cyclone‑dds (which has already been built)
WORKDIR /app/unitree_ros2/cyclonedds_ws
RUN bash -c "source /opt/ros/foxy/setup.bash && \
             pwd && \
             colcon build"
# Double check whether the build was successful
RUN ls -l /app/unitree_ros2/cyclonedds_ws
# ===== Installing unitree_ros2 =====


# Create a dedicated directory for your application code
WORKDIR /app

# Copy your docker_internal_setup.sh script into /app
COPY docker_internal_setup.sh .

# Ensure that docker_internal_setup.sh is executable
RUN chmod +x docker_internal_setup.sh

# Set the entrypoint to start your application
ENTRYPOINT ["./docker_internal_setup.sh"]
CMD ["bash"]