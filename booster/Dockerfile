# Use the official ROS Foxy Desktop image as a base (Ubuntu 20.04)
FROM osrf/ros:foxy-desktop

# Set an environment variable for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

# ============================================================================
# STEP 1/5: Install base dependencies
# ============================================================================
RUN echo "=========================================" && \
    echo "STEP 1/5: Installing base dependencies" && \
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
# STEP 2/5: Copy repository files
# ============================================================================
RUN echo "=========================================" && \
    echo "STEP 2/5: Preparing to copy repository" && \
    echo "========================================="
COPY . /app
RUN echo "✓ Repository files copied to /app"


# ============================================================================
# STEP 3/5: Install GStreamer and dependencies
# ============================================================================
RUN echo "=========================================" && \
    echo "STEP 3/5: Installing GStreamer dependencies" && \
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
    pip3 install requests numpy Pillow scipy casadi && \
    echo "✓ Python dependencies installed successfully"

WORKDIR /app
RUN echo "Testing PyGObject installation..." && \
    python3 tests/test_gi.py && \
    echo "✓ PyGObject test passed"


# ============================================================================
# STEP 4/5: Install Booster SDK
# ============================================================================
# This installs the Booster SDK from the official GitHub repository.
# Repository: https://github.com/BoosterRobotics/booster_robotics_sdk
WORKDIR /root
RUN echo "=========================================" && \
    echo "STEP 4/5: Installing Booster SDK" && \
    echo "=========================================" && \
    apt-get update --allow-releaseinfo-change --allow-insecure-repositories && \
    apt-get install -y --allow-unauthenticated \
    git \
    git-lfs \
    build-essential \
    cmake \
    libssl-dev \
    libasio-dev \
    libtinyxml2-dev \
    lsb-release \
    && rm -rf /var/lib/apt/lists/* && \
    git lfs install && \
    echo "Cloning Booster Robotics SDK repository..." && \
    git clone https://github.com/BoosterRobotics/booster_robotics_sdk.git && \
    echo "✓ Repository cloned" && \
    cd booster_robotics_sdk && \
    echo "Checking repository structure..." && \
    ls -R lib || echo "lib directory missing" && \
    echo "Fixing library paths for Ubuntu 20.04..." && \
    mkdir -p lib/x86_64/20 && \
    mkdir -p third_party/lib/x86_64/20 && \
    # If the libraries are in the parent directory (flat structure), copy them to the '20' subdirectory
    if [ -f lib/x86_64/libbooster_robotics_sdk.a ]; then \
        echo "Found libs in lib/x86_64, copying to lib/x86_64/20..." && \
        cp lib/x86_64/*.a lib/x86_64/20/ 2>/dev/null || true; \
    fi && \
    if [ -d third_party/lib/x86_64 ]; then \
        echo "Copying third_party libs to versioned dir..." && \
        cp -r third_party/lib/x86_64/* third_party/lib/x86_64/20/ 2>/dev/null || true; \
    fi && \
    echo "Running install.sh..." && \
    chmod +x install.sh && \
    ./install.sh && \
    echo "✓ Booster SDK installed successfully" && \
    cd .. && \
    rm -rf booster_robotics_sdk


# ============================================================================
# STEP 5/5: Build Booster ROS 2 Interface
# ============================================================================
# This step builds the ROS 2 interface package for Booster robots.
# Repository: https://github.com/BoosterRobotics/booster_robotics_sdk_ros2
WORKDIR /app/booster_ws/src
RUN echo "=========================================" && \
    echo "STEP 5/5: Building Booster ROS 2 Interface" && \
    echo "=========================================" && \
    echo "Cloning booster_robotics_sdk_ros2 repository..." && \
    git clone https://github.com/BoosterRobotics/booster_robotics_sdk_ros2.git && \
    echo "✓ Repository cloned" && \
    cd .. && \
    echo "Building ROS 2 workspace..." && \
    bash -c "source /opt/ros/foxy/setup.bash && \
             colcon build --packages-select booster_ros2_interface && \
             echo '✓ booster_ros2_interface package built successfully'"

# ============================================================================
# Final setup and configuration
# ============================================================================
WORKDIR /app

RUN echo "=========================================" && \
    echo "Final setup and configuration" && \
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
    echo "✓ Booster SDK installed" && \
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
