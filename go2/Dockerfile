# Use the official ROS Foxy Desktop image as a base (Ubuntu 20.04)
FROM osrf/ros:foxy-desktop

# Set an environment variable for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

# ============================================================================
# STEP 1/7: Install base dependencies
# ============================================================================
RUN echo "=========================================" && \
    echo "STEP 1/7: Installing base dependencies" && \
    echo "=========================================" && \
    # Force update with insecure repositories allowed to bypass GPG errors
    apt-get update --allow-releaseinfo-change --allow-insecure-repositories && \
    apt-get install -y --allow-unauthenticated \
    python3-pip \
    iputils-ping \
    git \
    vim \
    ros-foxy-rmw-cyclonedds-cpp \
    ros-foxy-rosidl-generator-dds-idl \
    ros-foxy-cv-bridge \
    ros-foxy-message-filters \
    ros-foxy-rqt-image-view \
    ros-foxy-image-view \
    xvfb \
    x11-apps \
    x11-xserver-utils \
    && rm -rf /var/lib/apt/lists/* && \
    echo "✓ Base dependencies installed successfully"

# ============================================================================
# STEP 2/7: Copy repository files
# ============================================================================
RUN echo "=========================================" && \
    echo "STEP 2/7: Preparing to copy repository" && \
    echo "========================================="
COPY . /app
RUN echo "✓ Repository files copied to /app"


# ============================================================================
# STEP 3/7: Install GStreamer and dependencies
# ============================================================================
RUN echo "=========================================" && \
    echo "STEP 3/7: Installing GStreamer dependencies" && \
    echo "=========================================" && \
    apt-get update --allow-releaseinfo-change --allow-insecure-repositories && \
    apt-get install -y --allow-unauthenticated \
    python3 \
    python3-pip \
    python3-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    pkg-config \
    gir1.2-gtk-3.0 \
    libgstreamer1.0-dev \
    gir1.2-gstreamer-1.0 \
    && rm -rf /var/lib/apt/lists/* && \
    echo "✓ GStreamer system packages installed"

RUN echo "Installing PyGObject via pip..." && \
    pip3 install PyGObject && \
    echo "✓ PyGObject installed successfully"

RUN echo "Installing Python dependencies for ROS2 scripts..." && \
    pip3 install requests "numpy>=1.19.5,<1.27.0" Pillow scipy casadi grpcio==1.62.0 grpcio-tools==1.62.0 "protobuf>=4.21.6" flask && \
    echo "✓ Python dependencies installed successfully"

WORKDIR /app
RUN echo "Testing PyGObject installation..." && \
    python3 tests/test_gi.py && \
    echo "✓ PyGObject test passed"


# ============================================================================
# STEP 4/7: Build and install unitree_sdk2
# ============================================================================
# This step builds the Unitree SDK2 C++ library which provides low-level
# communication with the Go2 robot. This may take several minutes.
WORKDIR /app/unitree_sdk2
RUN echo "=========================================" && \
    echo "STEP 4/7: Building unitree_sdk2" && \
    echo "=========================================" && \
    echo "Initializing submodules..." && \
    git submodule update --init --recursive && \
    echo "Creating build directory..." && \
    mkdir -p build && \
    cd build && \
    echo "Running cmake configuration..." && \
    cmake .. && \
    echo "Compiling unitree_sdk2 (this may take a few minutes)..." && \
    sudo make install && \
    echo "✓ unitree_sdk2 built and installed successfully"


# ============================================================================
# STEP 5/7: Build unitree_ros2 workspace
# ============================================================================
# This step sets up the ROS2 workspace with CycloneDDS and unitree_ros2 packages.
# Following: https://github.com/unitreerobotics/unitree_ros2
# This is the longest step and may take 10-20 minutes.
WORKDIR /app/unitree_ros2/cyclonedds_ws/src
RUN echo "=========================================" && \
    echo "STEP 5/7: Building unitree_ros2 workspace" && \
    echo "=========================================" && \
    echo "Cloning rmw_cyclonedds repository..." && \
    git clone https://github.com/ros2/rmw_cyclonedds -b foxy && \
    echo "✓ rmw_cyclonedds cloned" && \
    echo "Cloning cyclonedds repository..." && \
    git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x && \
    echo "✓ cyclonedds cloned"

RUN echo "Building cyclonedds package (this may take several minutes)..." && \
    cd /app/unitree_ros2/cyclonedds_ws && \
    colcon build --packages-select cyclonedds && \
    echo "✓ cyclonedds built successfully"

WORKDIR /app/unitree_ros2/cyclonedds_ws
RUN echo "Building remaining unitree_ros2 packages (this may take 10-20 minutes)..." && \
    bash -c "source /opt/ros/foxy/setup.bash && \
             echo 'Current directory: ' && pwd && \
             echo 'Starting colcon build...' && \
             colcon build && \
             echo '✓ All unitree_ros2 packages built successfully'"

RUN echo "Verifying build output..." && \
    ls -lh /app/unitree_ros2/cyclonedds_ws/install && \
    echo "✓ Build verification complete"


# ============================================================================
# STEP 6/7: Install unitree_sdk2_python
# ============================================================================
# This installs the Python bindings for unitree_sdk2, allowing Python scripts
# to interact with the Go2 robot.
WORKDIR /root
RUN echo "=========================================" && \
    echo "STEP 6/7: Installing unitree_sdk2_python" && \
    echo "=========================================" && \
    echo "pip3 should already be available in base image" && \
    pip3 --version && \
    echo "Cloning unitree_sdk2_python repository..." && \
    git clone https://github.com/unitreerobotics/unitree_sdk2_python.git && \
    echo "✓ Repository cloned" && \
    cd unitree_sdk2_python && \
    echo "Installing unitree_sdk2_python package..." && \
    pip3 install -e . && \
    echo "✓ unitree_sdk2_python installed successfully"


# ============================================================================
# STEP 7/7: Final setup and configuration
# ============================================================================
WORKDIR /app

RUN echo "=========================================" && \
    echo "STEP 7/7: Final setup and configuration" && \
    echo "========================================="

# Copy your docker_internal_setup.sh script into /app
COPY docker_internal_setup.sh .

RUN echo "Configuring Python and pip aliases..." && \
    rm -f /usr/bin/pip && ln -sf /usr/bin/pip3 /usr/bin/pip && \
    rm -f /usr/bin/python && ln -sf /usr/bin/python3 /usr/bin/python && \
    echo "✓ Python aliases configured" && \
    echo "Making docker_internal_setup.sh executable..." && \
    chmod +x docker_internal_setup.sh && \
    echo "✓ Setup script is executable"

RUN echo "=========================================" && \
    echo "Build Summary:" && \
    echo "=========================================" && \
    echo "✓ Base dependencies installed" && \
    echo "✓ GStreamer and PyGObject installed" && \
    echo "✓ unitree_sdk2 built and installed" && \
    echo "✓ unitree_ros2 workspace built" && \
    echo "✓ unitree_sdk2_python installed" && \
    echo "✓ Final configuration complete" && \
    echo "=========================================" && \
    echo "Docker image build completed successfully!" && \
    echo "=========================================" && \
    python3 --version && \
    pip3 --version && \
    echo "Ready to run the container!"

# Set the entrypoint to start your application
ENTRYPOINT ["./docker_internal_setup.sh"]
CMD ["bash"]

